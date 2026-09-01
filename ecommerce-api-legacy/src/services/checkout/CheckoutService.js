const { AppError } = require('../../shared/errors/AppError');
const { hashPassword } = require('../../models/users/passwordHash');

class CheckoutService {
  constructor(dependencies) { Object.assign(this, dependencies); }
  async checkout(payload) {
    const course = await this.courseRepository.findActiveById(payload.courseId);
    if (!course) throw new AppError(404, 'Curso não encontrado');
    const user = await this.userRepository.findByEmail(payload.email);
    const paymentStatus = payload.card.startsWith('4') ? 'PAID' : 'DENIED';
    this.logger.info('Processando pagamento', { courseId: payload.courseId });
    if (paymentStatus === 'DENIED') throw new AppError(400, 'Pagamento recusado');

    return this.checkoutRepository.transaction(async (tx) => {
      let userId = user?.id;
      if (!userId) {
        const created = await this.userRepository.create({
          name: payload.userName,
          email: payload.email,
          passwordHash: hashPassword(payload.password)
        }, tx);
        userId = created.lastID;
      }
      const enrollment = await this.checkoutRepository.createEnrollment(userId, payload.courseId, tx);
      await this.checkoutRepository.createPayment(enrollment.lastID, course.price, paymentStatus, tx);
      await this.checkoutRepository.createAuditLog(`Checkout curso ${payload.courseId} por ${userId}`, tx);
      return { msg: 'Sucesso', enrollment_id: enrollment.lastID };
    });
  }
}

module.exports = { CheckoutService };
