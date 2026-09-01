function validateCheckoutPayload(body) {
  const payload = body && typeof body === 'object' ? body : {};
  const value = {
    userName: payload.usr,
    email: payload.eml,
    password: payload.pwd,
    courseId: payload.c_id,
    card: payload.card
  };
  if (!value.userName || !value.email || !value.courseId || !value.card) return { error: 'Bad Request' };
  if (typeof value.userName !== 'string' || typeof value.email !== 'string' ||
      !Number.isInteger(value.courseId) || value.courseId < 1 || typeof value.card !== 'string') {
    return { error: 'Bad Request' };
  }
  return { value };
}

module.exports = { validateCheckoutPayload };
