
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import AdminIndexView
from flask import redirect, url_for, flash
from flask_login import current_user
from app.models.models import db, User, NobleRank, Transaction, MoneyAccount, GoldAccount, NobleRelation
from app.services.noble_rank_service import NobleRankService
import logging
from datetime import datetime
from decimal import Decimal

class SecureBaseView(BaseView):
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
    column_list = ['id', 'username', 'email', 'money_account.balance', 'gold_account.balance', 'noble_rank.rank']
    column_searchable_list = ['username', 'email']
    column_filters = ['noble_rank.rank']
    
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

admin = Admin(name='Gold Investment Admin', template_mode='bootstrap3')

admin.add_view(DashboardView(name='Dashboard', endpoint='admin'))
admin.add_view(ClientView(User, db.session, name='Clients'))
admin.add_view(TransactionView(Transaction, db.session, name='Transactions'))
admin.add_view(NetworkView(name='Affiliate Network', endpoint='network'))
admin.add_view(AccountingView(name='Accounting', endpoint='accounting'))
