from django.contrib.auth.decorators import user_passes_test

def main_admin_required(view_func):
    def check_main_admin(user):
        return user.is_authenticated and user.user_type == 'admin' and not user.is_sub_admin
    return user_passes_test(check_main_admin)(view_func)

def admin_required(view_func):
    def check_admin(user):
        return user.is_authenticated and user.user_type == 'admin'
    return user_passes_test(check_admin)(view_func)