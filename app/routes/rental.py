from fastapi import APIRouter, Depends, HTTPException, Request, Form, UploadFile, File
from typing import List
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from app.dbfactory import get_db
from app.model.regions import Region
from app.schema.rental import NewRental
from app.service.rental import RentalService, get_rental_data, process_upload

rental_router = APIRouter()
templates = Jinja2Templates(directory='views/templates')

@rental_router.get('/', response_class=HTMLResponse)
async def rental(req: Request, db: Session = Depends(get_db)):
    try:
        rentals = RentalService.select_rentals(db)
        regions = db.query(Region).all()  # 지역 정보 가져오기
        return templates.TemplateResponse('rental/rental.html', {'request': req, 'rentals': rentals, 'regions': regions})
    except Exception as ex:
        print(f'▷▷▷ rental 오류 발생 : {str(ex)}')
        raise HTTPException(status_code=500, detail="Internal Server Error")

# 렌탈 항목 추가 폼 페이지
@rental_router.get("/add", response_class=HTMLResponse)
async def read_add(request: Request, db: Session = Depends(get_db)):
    try:
        regions = db.query(Region).all()  # 지역 정보를 데이터베이스에서 가져옴
        return templates.TemplateResponse("rental/add.html", {"request": request, "regions": regions})
    except Exception as ex:
        print(f'오류 발생: {str(ex)}')
        raise HTTPException(status_code=500, detail="Internal Server Error")

# 렌탈 항목 추가 처리
@rental_router.post("/add", response_class=HTMLResponse)
async def add_rental(request: Request, rental: NewRental = Depends(get_rental_data),
                     files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    try:
        attachs = await process_upload(files)
        if RentalService.insert_rental(rental, attachs, db):
            return RedirectResponse('/rental/', status_code=303)
    except Exception as ex:
        print(f'▷▷▷ add_rental 오류 발생 : {str(ex)}')
        raise HTTPException(status_code=500, detail="Internal Server Error")

# 렌탈 항목 상세 보기
@rental_router.get('/details/{spaceno}', response_class=HTMLResponse)
async def detail_rental(req: Request, spaceno: int, db: Session = Depends(get_db)):
    try:
        rent = RentalService.select_one_rental(spaceno, db)
        return templates.TemplateResponse('rental/details.html', {'request': req, 'rent': rent})
    except Exception as ex:
        print(f'▷▷▷ detail_rental 오류 발생 : {str(ex)}')
        raise HTTPException(status_code=500, detail="Internal Server Error")
