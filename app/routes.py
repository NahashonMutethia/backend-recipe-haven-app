from flask import Blueprint, request, jsonify
from app import db
from app.models import Recipe, Review
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('routes', __name__)

@bp.route('/recipes', methods=['POST'])
@jwt_required()
def create_recipe():
    data = request.get_json()
    user_id = get_jwt_identity()
    recipe = Recipe(
        title=data['title'],
        ingredients=data['ingredients'],
        steps=data['steps'],
        image_url=data.get('image_url'),
        category=data.get('category'),
        user_id=user_id
    )
    db.session.add(recipe)
    db.session.commit()
    return jsonify({'message': 'Recipe created successfully'}), 201

@bp.route('/recipes', methods=['GET'])
def get_recipes():
    recipes = Recipe.query.all()
    return jsonify([recipe.to_dict() for recipe in recipes])

@bp.route('/recipes/<int:id>', methods=['GET'])
def get_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    return jsonify(recipe.to_dict())

@bp.route('/recipes/<int:id>', methods=['PUT'])
@jwt_required()
def update_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    user_id = get_jwt_identity()
    if recipe.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.get_json()
    recipe.title = data['title']
    recipe.ingredients = data['ingredients']
    recipe.steps = data['steps']
    recipe.image_url = data.get('image_url')
    recipe.category = data.get('category')
    db.session.commit()
    return jsonify({'message': 'Recipe updated successfully'})

@bp.route('/recipes/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    user_id = get_jwt_identity()
    if recipe.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    db.session.delete(recipe)
    db.session.commit()
    return jsonify({'message': 'Recipe deleted successfully'})

@bp.route('/recipes/<int:id>/reviews', methods=['POST'])
@jwt_required()
def create_review(id):
    data = request.get_json()
    user_id = get_jwt_identity()
    review = Review(
        rating=data['rating'],
        comment=data['comment'],
        user_id=user_id,
        recipe_id=id
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({'message': 'Review created successfully'}), 201

@bp.route('/recipes/<int:id>/reviews', methods=['GET'])
def get_reviews(id):
    reviews = Review.query.filter_by(recipe_id=id).all()
    return jsonify([review.to_dict() for review in reviews])

@bp.errorhandler(400)
def bad_request(error):
    return jsonify({'message': 'Bad request'}), 400

@bp.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Resource not found'}), 404

@bp.errorhandler(500)
def internal_server_error(error):
    return jsonify({'message': 'Internal server error'}), 500
