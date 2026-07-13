from fastapi import Request, HTTPException, status
from security import decode_access_token

COOKIE_NAME = "access_token"


def get_current_member(request: Request) -> dict:
    """
    인증이 필요한 엔드포인트에 Depends(get_current_member)로 붙여서 사용.
    쿠키의 JWT를 검증해서 회원 정보(payload)를 반환하고,
    쿠키가 없거나 토큰이 유효하지 않으면 401을 던진다.
    """
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "로그인이 필요합니다."},
        )

    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "세션이 만료되었거나 유효하지 않습니다."},
        )

    return payload  # {"member_id": ..., "email": ..., "nickname": ..., "iat": ..., "exp": ...}
