from functools import wraps

from core.utils.exceptions import ActionException


def exc_handler_false(funct):
    @wraps(funct)
    def _wrapper(obj, message):
        try:
            return funct(obj, message)
        except:
            params = {"message": message}
            return False
    return _wrapper


def exc_handler(funct):
    @wraps(funct)
    def _wrapper(obj, *args, **kwargs):
        try:
            return funct(obj, *args, **kwargs)
        except ActionException:
            """  Данное исключение вызывается в методе field_check, при проверке наличия полей сообщения, 
            там же, в случае отсутсвия поля, вызывается соответствующий system_log.
                 ActionException обрабатываем в MaestroModel.run_one и отправляем метрику."""
            pass
        except Exception as e:
            params = {
                "method": funct.__name__,
                "args": args,
                "kwargs": kwargs
            }
            raise e
    return _wrapper