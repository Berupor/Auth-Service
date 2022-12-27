from fastapi import APIRouter, Response, status

from src.api.decorators import auth, trace


router = APIRouter()


@router.get(
    "/search/",
    status_code=status.HTTP_200_OK,
    summary="Поиск фильмов",
)
@trace()
@auth(permissions=["can_view_film"])
async def search(
    response: Response,
):

    #  Подразумеваем, что каждый endpoint формирует
    #  2 варианта данных - с деградацией и без, и отдает
    #  декоратору, который решает, что возвратить на
    #  основании ответов от сервиса авторизации

    actual_info = {"data": "Info without degradation"}
    degradated_info = {"data": "Gracefully degradated info"}

    return actual_info, degradated_info
