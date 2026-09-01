from __future__ import annotations

from flask import Flask
from flask_cors import CORS

from controllers.categories import CategoryController
from controllers.reports import ReportController
from controllers.tasks import TaskController
from controllers.users import UserController
from models import Category, Task, User  # noqa: F401 — registra Models no SQLAlchemy
from repositories.categories import CategoryRepository
from repositories.reports import ReportRepository
from repositories.tasks import TaskRepository
from repositories.users import UserRepository
from routes.categories import create_category_blueprint
from routes.reports import create_report_blueprint
from routes.tasks import create_task_blueprint
from routes.users import create_user_blueprint
from services.reports import ReportService
from services.tasks import TaskService
from services.users import AuthService, UserService
from shared.auth import AuthMiddleware
from shared.config import load_config
from shared.database import db
from shared.errors import register_error_handlers
from shared.time import utc_now


def create_app(config: dict | None = None) -> Flask:
    application = Flask(__name__)
    application.config.from_mapping(load_config())
    if config:
        application.config.from_mapping(config)

    CORS(application)
    db.init_app(application)
    register_error_handlers(application)

    user_repository = UserRepository(db.session)
    auth_service = AuthService(
        user_repository,
        application.config["SECRET_KEY"],
        application.config["TOKEN_MAX_AGE"],
    )
    auth_middleware = AuthMiddleware(auth_service)

    task_controller = TaskController(TaskService(TaskRepository(db.session)))
    user_controller = UserController(UserService(user_repository), auth_service)
    category_controller = CategoryController(CategoryRepository(db.session))
    report_controller = ReportController(ReportService(ReportRepository(db.session)))

    application.register_blueprint(create_task_blueprint(task_controller, auth_middleware))
    application.register_blueprint(create_user_blueprint(user_controller, auth_middleware))
    application.register_blueprint(
        create_category_blueprint(category_controller, auth_middleware)
    )
    application.register_blueprint(
        create_report_blueprint(report_controller, auth_middleware)
    )

    @application.get("/health")
    def health():
        return {"status": "ok", "timestamp": str(utc_now())}

    @application.get("/")
    def index():
        return {"message": "Task Manager API", "version": "1.0"}

    @application.cli.command("init-db")
    def init_db_command() -> None:
        """Cria o schema explicitamente; não é executado durante importação."""

        db.create_all()
        print("Banco inicializado.")

    return application


app = create_app()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(
        debug=app.config["DEBUG"],
        host=app.config["APP_HOST"],
        port=app.config["APP_PORT"],
    )
