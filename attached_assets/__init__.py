
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_required
from flask import redirect, url_for, flash
from app.models.models import (db, User, Transaction, MoneyAccount, 
                             GoldAccount, GoldBar, NobleRank, NobleRelation)

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        flash('Please log in with admin privileges', 'error')
        return redirect(url_for('auth.login'))

class AdminHomeView(AdminIndexView):
    @expose('/')
    @login_required
    def index(self):
        if not current_user.is_admin:
            return redirect(url_for('auth.login'))
        stats = {
            'total_users': User.query.count(),
            'total_transactions': Transaction.query.count(),
            'total_gold_bars': GoldBar.query.count()
        }
        return self.render('admin/dashboard.html', stats=stats)

admin = Admin(name='Gold Investment Admin', 
             index_view=AdminHomeView(), 
             template_mode='bootstrap3')

# Register views
admin.add_view(SecureModelView(User, db.session, name='Users'))
admin.add_view(SecureModelView(MoneyAccount, db.session, name='Money Accounts'))
admin.add_view(SecureModelView(GoldAccount, db.session, name='Gold Accounts'))
admin.add_view(SecureModelView(GoldBar, db.session, name='Gold Bars'))
admin.add_view(SecureModelView(NobleRank, db.session, name='Noble Ranks'))
admin.add_view(SecureModelView(NobleRelation, db.session, name='Noble Relations'))
admin.add_view(SecureModelView(Transaction, db.session, name='Transactions'))
