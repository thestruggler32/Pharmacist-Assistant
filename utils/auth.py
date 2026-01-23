from functools import wraps
from flask import abort, request


USERS = {
    "pharma_001": {"role": "pharmacist", "name": "Dr. Smith"},
    "doctor_001": {"role": "doctor", "name": "Dr. Johnson"},
    "patient_001": {"role": "patient", "name": "John Doe"},
    "admin_001": {"role": "admin", "name": "Admin User"}
}


def get_current_user():
    """Get hardcoded current user (demo only)"""
    user_id = request.args.get('user_id', 'pharma_001')
    return USERS.get(user_id, {"role": "pharmacist", "id": "pharma_001"})


def role_required(allowed_roles):
    """Decorator to enforce role-based access control"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if user.get("role") not in allowed_roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
