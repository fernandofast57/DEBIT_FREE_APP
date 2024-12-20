
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import AdminIndexView
from flask import redirect, url_for, flash
from flask_login import current_user
from app.models.models import db, User, NobleRank, Transaction
import logging
from datetime import datetime

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def after_model_change(self, form, model, is_created):
        logging.info(f'Admin action: {"created" if is_created else "modified"} {model.__class__.__name__} ID:{model.id} by {current_user.email}')

    def after_model_delete(self, model):
        logging.info(f'Admin action: deleted {model.__class__.__name__} ID:{model.id} by {current_user.email}')

class TransactionView(SecureModelView):
    can_delete = False  # Impedisce l'eliminazione delle transazioni
    can_create = False  # Solo il sistema può creare transazioni
    can_edit = False   # Le transazioni non possono essere modificate
    
    column_list = ['id', 'user_id', 'amount', 'status', 'created_at', 'validation_date', 'validated_by']
    column_searchable_list = ['user_id', 'status']
    column_filters = ['status', 'created_at', 'validation_date']
    
    def _format_amount(view, context, model, name):
        return f"€ {model.amount:,.2f}"
    
    column_formatters = {
        'amount': _format_amount
    }

class AuditLogView(BaseView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('auth.login'))
            
        with open('logs/admin_audit.log', 'r') as f:
            audit_logs = f.readlines()[-100:]  # Ultimi 100 log
        return self.render('admin/audit_log.html', logs=audit_logs)

admin = Admin(name='Gold Investment Admin', template_mode='bootstrap3',
             index_view=AdminIndexView())

admin.add_view(SecureModelView(User, db.session))
admin.add_view(SecureModelView(NobleRank, db.session))
admin.add_view(TransactionView(Transaction, db.session))
admin.add_view(AuditLogView(name='Audit Log', endpoint='audit'))
