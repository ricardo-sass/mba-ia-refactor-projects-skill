const { AppError } = require('../../shared/errors/AppError');
const { validateCheckoutPayload } = require('../../models/checkout/checkoutPayload');

class CheckoutController {
  constructor(service) { this.service = service; }
  async checkout(body) {
    const validation = validateCheckoutPayload(body);
    if (validation.error) throw new AppError(400, validation.error);
    return this.service.checkout(validation.value);
  }
}

module.exports = { CheckoutController };
