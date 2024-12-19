
from flask import Blueprint, jsonify, request
from app.models.models import User, NobleRank
from app.utils.auth import auth_required
from app.utils.security.rate_limiter import rate_limit

bp = Blueprint('noble', __name__)

@bp.route('/rank', methods=['GET'])
@auth_required
@rate_limit(requests=10, window=60)
def get_user_rank():
    """Get current user's noble rank"""
    user_id = request.user_id
    user = User.query.get(user_id)
    
    if not user or not user.noble_rank:
        return jsonify({'rank': None, 'next_rank': 'Knight'})
        
    return jsonify({
        'current_rank': user.noble_rank.rank_name,
        'investment_amount': float(user.total_investment),
        'next_rank': user.noble_rank.next_rank_name
    })

@bp.route('/requirements', methods=['GET'])
@auth_required
@rate_limit(requests=10, window=60)
def get_rank_requirements():
    """Get requirements for all noble ranks"""
    ranks = NobleRank.query.all()
    requirements = {
        rank.rank_name: {
            'min_investment': float(rank.min_investment),
            'bonus_rate': float(rank.bonus_rate)
        } for rank in ranks
    }
    return jsonify(requirements)
