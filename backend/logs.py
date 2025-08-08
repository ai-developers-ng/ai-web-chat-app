from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, SearchLog, UserAction, LoginLog
from sqlalchemy import desc
from datetime import datetime, timedelta
import time

logs_bp = Blueprint('logs', __name__)

def log_search(search_type, query, response=None, response_time=None):
    """Log a search/query activity"""
    if current_user.is_authenticated:
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
        user_agent = request.headers.get('User-Agent', 'unknown')
        
        search_log = SearchLog(
            user_id=current_user.id,
            search_type=search_type,
            query=query,
            response=response,
            response_time=response_time,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(search_log)
        db.session.commit()
        return search_log.id
    return None

def log_user_action(action_type, details=None):
    """Log a user action"""
    if current_user.is_authenticated:
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
        user_agent = request.headers.get('User-Agent', 'unknown')
        
        action = UserAction(
            user_id=current_user.id,
            action_type=action_type,
            ip_address=ip_address,
            user_agent=user_agent
        )
        if details:
            action.set_details(details)
        db.session.add(action)
        db.session.commit()
        return action.id
    return None

@logs_bp.route('/searches', methods=['GET'])
@login_required
def get_search_logs():
    """Get user's search history"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search_type = request.args.get('type')  # Filter by search type
        
        # Limit per_page to prevent abuse
        per_page = min(per_page, 100)
        
        query = db.select(SearchLog).filter_by(user_id=current_user.id)
        
        if search_type:
            query = query.filter_by(search_type=search_type)
        
        query = query.order_by(desc(SearchLog.timestamp))
        
        searches = db.paginate(query,
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'searches': [search.to_dict() for search in searches.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': searches.total,
                'pages': searches.pages,
                'has_next': searches.has_next,
                'has_prev': searches.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get search logs: {str(e)}'}), 500

@logs_bp.route('/actions', methods=['GET'])
@login_required
def get_user_actions():
    """Get user's action history"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        action_type = request.args.get('type')  # Filter by action type
        
        # Limit per_page to prevent abuse
        per_page = min(per_page, 100)
        
        query = db.select(UserAction).filter_by(user_id=current_user.id)
        
        if action_type:
            query = query.filter_by(action_type=action_type)
        
        query = query.order_by(desc(UserAction.timestamp))
        
        actions = db.paginate(query,
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'actions': [action.to_dict() for action in actions.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': actions.total,
                'pages': actions.pages,
                'has_next': actions.has_next,
                'has_prev': actions.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get user actions: {str(e)}'}), 500

@logs_bp.route('/logins', methods=['GET'])
@login_required
def get_login_logs():
    """Get user's login history"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Limit per_page to prevent abuse
        per_page = min(per_page, 100)
        
        query = db.select(LoginLog).filter_by(user_id=current_user.id)
        query = query.order_by(desc(LoginLog.login_time))
        
        logins = db.paginate(query,
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'logins': [login.to_dict() for login in logins.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': logins.total,
                'pages': logins.pages,
                'has_next': logins.has_next,
                'has_prev': logins.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get login logs: {str(e)}'}), 500

@logs_bp.route('/stats', methods=['GET'])
@login_required
def get_user_stats():
    """Get user activity statistics"""
    try:
        # Get date range (default to last 30 days)
        days = request.args.get('days', 30, type=int)
        days = min(days, 365)  # Limit to 1 year
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Search statistics
        search_stats_query = db.select(
            SearchLog.search_type,
            db.func.count(SearchLog.id).label('count')
        ).filter(
            SearchLog.user_id == current_user.id,
            SearchLog.timestamp >= start_date
        ).group_by(SearchLog.search_type)
        search_stats = db.session.execute(search_stats_query).all()
        
        # Action statistics
        action_stats_query = db.select(
            UserAction.action_type,
            db.func.count(UserAction.id).label('count')
        ).filter(
            UserAction.user_id == current_user.id,
            UserAction.timestamp >= start_date
        ).group_by(UserAction.action_type)
        action_stats = db.session.execute(action_stats_query).all()
        
        # Login statistics
        login_stats_query = db.select(
            db.func.count(LoginLog.id).label('total_logins'),
            db.func.sum(db.case((LoginLog.success == True, 1), else_=0)).label('successful_logins'),
            db.func.sum(db.case((LoginLog.success == False, 1), else_=0)).label('failed_logins')
        ).filter(
            LoginLog.user_id == current_user.id,
            LoginLog.login_time >= start_date
        )
        login_stats = db.session.execute(login_stats_query).first()
        
        # Recent activity count
        recent_searches = db.session.scalar(db.select(db.func.count()).select_from(SearchLog).filter(
            SearchLog.user_id == current_user.id,
            SearchLog.timestamp >= start_date
        ))
        
        recent_actions = db.session.scalar(db.select(db.func.count()).select_from(UserAction).filter(
            UserAction.user_id == current_user.id,
            UserAction.timestamp >= start_date
        ))
        
        return jsonify({
            'period_days': days,
            'search_stats': {
                'by_type': [{'type': stat[0], 'count': stat[1]} for stat in search_stats],
                'total': recent_searches
            },
            'action_stats': {
                'by_type': [{'type': stat[0], 'count': stat[1]} for stat in action_stats],
                'total': recent_actions
            },
            'login_stats': {
                'total_logins': login_stats.total_logins or 0,
                'successful_logins': login_stats.successful_logins or 0,
                'failed_logins': login_stats.failed_logins or 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get user stats: {str(e)}'}), 500

@logs_bp.route('/export', methods=['GET'])
@login_required
def export_user_data():
    """Export all user data"""
    try:
        export_type = request.args.get('type', 'all')  # 'searches', 'actions', 'logins', 'all'
        
        data = {}
        
        if export_type in ['searches', 'all']:
            searches_query = db.select(SearchLog).filter_by(user_id=current_user.id).order_by(desc(SearchLog.timestamp))
            searches = db.session.execute(searches_query).scalars().all()
            data['searches'] = [search.to_dict() for search in searches]
        
        if export_type in ['actions', 'all']:
            actions_query = db.select(UserAction).filter_by(user_id=current_user.id).order_by(desc(UserAction.timestamp))
            actions = db.session.execute(actions_query).scalars().all()
            data['actions'] = [action.to_dict() for action in actions]
        
        if export_type in ['logins', 'all']:
            logins_query = db.select(LoginLog).filter_by(user_id=current_user.id).order_by(desc(LoginLog.login_time))
            logins = db.session.execute(logins_query).scalars().all()
            data['logins'] = [login.to_dict() for login in logins]
        
        data['user'] = current_user.to_dict()
        data['export_timestamp'] = datetime.utcnow().isoformat()
        
        # Log the export action
        log_user_action('data_export', {'export_type': export_type})
        
        return jsonify(data), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to export data: {str(e)}'}), 500

# Utility function to be used in other modules
def create_search_log_decorator(search_type):
    """Decorator factory to automatically log searches"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Get the query from request
            if request.is_json:
                data = request.get_json()
                query = data.get('message') or data.get('prompt') or str(data)
            else:
                query = str(request.form) if request.form else str(request.args)
            
            try:
                result = func(*args, **kwargs)
                response_time = time.time() - start_time
                
                # Extract response text if it's a JSON response
                response_text = None
                if hasattr(result, 'get_json'):
                    json_data = result.get_json()
                    if json_data and 'response' in json_data:
                        response_text = json_data['response']
                
                # Log the search
                log_search(search_type, query, response_text, response_time)
                
                return result
            except Exception as e:
                response_time = time.time() - start_time
                log_search(search_type, query, f"Error: {str(e)}", response_time)
                raise
        
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator
