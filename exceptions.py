class NotFoundRecordException(Exception):
    code = 404
    error_code = 404
    message = 'record not found'


class RecordIsExistsException(Exception):
    code = 409
    error_code = 409
    message = 'record is already exists'
