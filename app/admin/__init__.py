
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import AdminIndexView
from flask import redirect, url_for, flash
from flask_login import current_user
from app.models.models import db, User, Transaction, MoneyAccount, GoldAccount, NobleRelation, GoldBar
from app.models.noble_system import NobleRank
from app.services.noble_rank_service import NobleRankService
import logging
from datetime import datetime
from decimal import Decimal


class SecureBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin


class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin


class DashboardView(SecureBaseView):
    @expose('/')
    def index(self):
        total_gold = db.session.query(db.func.sum(GoldAccount.balance)).scalar() or 0
        total_money = db.session.query(db.func.sum(MoneyAccount.balance)).scalar() or 0
        total_users = User.query.count()

        return self.render('admin/dashboard.html',
                           total_gold=total_gold,
                           total_money=total_money,
                           total_users=total_users)


class ClientView(SecureModelView):
    column_list = ['id', 'username', 'email', 'money_account.balance', 'gold_account.balance']
    column_searchable_list = ['username', 'email']
    column_filters = ['username', 'email']

    def _format_balance(view, context, model, name):
        if name == 'money_account.balance':
            return f"€ {model.money_account.balance:,.2f}" if model.money_account else "€ 0.00"
        return f"{model.gold_account.balance:,.4f}g" if model.gold_account else "0.0000g"

    column_formatters = {
        'money_account.balance': _format_balance,
        'gold_account.balance': _format_balance
    }


class NetworkView(SecureBaseView):
    @expose('/')
    def index(self):
        network_data = NobleRankService.get_complete_network()
        return self.render('admin/network.html', network=network_data)


class AccountingView(SecureBaseView):
    @expose('/')
    def index(self):
        transactions = Transaction.query.order_by(Transaction.timestamp.desc()).limit(100)
        return self.render('admin/accounting.html', transactions=transactions)


class GoldBarView(SecureModelView):
    column_list = ['serial_number', 'weight_grams', 'location', 'status']
    column_searchable_list = ['serial_number', 'status']
    column_filters = ['status', 'location']

    def _format_weight(view, context, model, name):
        return f"{model.weight_grams:,.2f}g"

    column_formatters = {
        'weight_grams': _format_weight
    }


class KYCView(SecureModelView):
    column_list = ['user.username', 'verification_status', 'document_type', 'document_number', 'verification_date']
    column_searchable_list = ['verification_status', 'document_number']
    column_filters = ['verification_status', 'document_type']
    can_delete = False


admin = Admin(name='Gold Investment Admin', template_mode='bootstrap3')

admin.add_view(DashboardView(name='Dashboard', endpoint='admin'))
admin.add_view(ClientView(User, db.session, name='Clients'))
admin.add_view(AccountingView(name='Accounting', endpoint='accounting'))
admin.add_view(NetworkView(name='Affiliate Network', endpoint='network'))
admin.add_view(GoldBarView(GoldBar, db.session, name='Gold Bars'))
admin.add_view(KYCView(NobleRelation, db.session, name='KYC Management'))
