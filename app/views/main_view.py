from flask import Blueprint, request, jsonify
from app.services.main_service import Anime


bp_animes = Blueprint('animes', __name__, url_prefix='/animes')


@bp_animes.route('', methods=['GET', 'POST'])
def get_create():

    data = request.get_json()
    method = request.method
    output, status_code = Anime.checking_method(method, data)
    return jsonify(output), status_code


@bp_animes.route('/<int:anime_id>')
def filter(anime_id):
    output, status_code = Anime.get_by_id(anime_id)
    return jsonify(output), status_code


@bp_animes.route('/<int:anime_id>', methods=['PATCH'])
def update(anime_id):
    data = request.get_json()
    output, status_code = Anime.update(anime_id, data)
    return output, status_code


@bp_animes.route('/<int:anime_id>', methods=['DELETE'])
def delete(anime_id):
    output, status_code = Anime.delete(anime_id)
    return output, status_code
