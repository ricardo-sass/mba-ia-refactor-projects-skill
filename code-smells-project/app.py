import os

from flask import Flask
from flask_cors import CORS

from controllers.catalogo import CatalogController
from controllers.operacional import OperationalController
from controllers.pedidos import OrderController
from controllers.relatorios import SalesReportController
from controllers.usuarios import UserController
from models.catalogo import CatalogModel
from models.usuarios import UserModel
from repositories.operacional import HealthRepository
from repositories.pedidos import OrderRepository
from repositories.relatorios import SalesReportRepository
from routes.catalogo import create_blueprint as create_catalog_blueprint
from routes.operacional import create_blueprint as create_operational_blueprint
from routes.pedidos import create_blueprint as create_order_blueprint
from routes.relatorios import create_blueprint as create_report_blueprint
from routes.usuarios import create_blueprint as create_user_blueprint
from services.pedidos import OrderService
from services.relatorios import SalesReportService
from services.usuarios import UserService
from shared.config import build_config
from shared.database import get_db, init_app as init_database
from shared.errors import register_error_handlers


def create_app(config=None):
    application = Flask(__name__)
    application.config.from_mapping(build_config(config))
    init_database(application)
    register_error_handlers(application)

    allowed_origins = application.config["CORS_ORIGINS"]
    if allowed_origins:
        CORS(application, origins=allowed_origins)

    catalog_model = CatalogModel(get_db)
    user_model = UserModel(get_db)
    order_repository = OrderRepository(get_db)
    report_repository = SalesReportRepository(get_db)
    health_repository = HealthRepository(get_db)

    catalog_controller = CatalogController(catalog_model)
    user_controller = UserController(user_model, UserService(user_model))
    order_controller = OrderController(
        order_repository,
        OrderService(order_repository, application.logger),
    )
    report_controller = SalesReportController(SalesReportService(report_repository))
    operational_controller = OperationalController(
        health_repository,
        application.config["APP_ENV"],
    )

    application.register_blueprint(create_catalog_blueprint(catalog_controller))
    application.register_blueprint(create_user_blueprint(user_controller))
    application.register_blueprint(create_order_blueprint(order_controller))
    application.register_blueprint(create_report_blueprint(report_controller))
    application.register_blueprint(create_operational_blueprint(operational_controller))
    return application


app = create_app()


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    app.run(host=host, port=port, debug=app.config["DEBUG"])
