from fastapi import APIRouter, Depends, Response

from src.model import Driver, Schedule
from src.parameters import pagination_parameters, DriverScheduleFilterParameters, TopDriversFilterParameters
from src.responses import TopDriver
from src.security import JWTBearer, roles
from src.services import DriverService


router = APIRouter()


DriverListResponse = Driver.get_pydantic(exclude={"schedules"})
@router.get("/", response_model=list[DriverListResponse], dependencies=[Depends(JWTBearer(roles.all))])
async def all(pagination_parameters=Depends(pagination_parameters)):
    page, page_size = pagination_parameters["page"], pagination_parameters["page_size"]
    drivers = await Driver.objects.paginate(page=page, page_size=page_size).all()
    return drivers


@router.get("/top_drivers", response_model=list[TopDriver], dependencies=[Depends(JWTBearer(roles.all))])
async def get_top_drivers(filters: TopDriversFilterParameters = Depends(TopDriversFilterParameters), driverService=Depends(DriverService)):
    drivers = await driverService.get_top_drivers(filters.weekDateBegin, filters.weekDateEnd)
    return drivers


DriverDetailsResponse = Driver.get_pydantic(
    exclude={"schedules"})
@router.get("/{driver_id}", response_model=DriverDetailsResponse, dependencies=[Depends(JWTBearer(roles.all))], responses={
    200: {"model": DriverDetailsResponse},
    404: {"description": "Driver not found"}}
)
async def get(driver_id: int, response: Response):
    driver = await Driver.objects.get_or_none(id=driver_id)
    if driver is None:
        response.status_code = 404
        return {"error": "Driver not found"}
    return driver


ScheduleResponse = Schedule.get_pydantic(exclude={"driver", "bus__schedules"})
@router.get("/{driver_id}/schedule", dependencies=[Depends(JWTBearer(roles.all))], response_model=list[ScheduleResponse])
async def get_schedule(driver_id: int, response: Response, filters: DriverScheduleFilterParameters = Depends(DriverScheduleFilterParameters), driverService=Depends(DriverService)):
    driver = await driverService.get_with_schedules_by_week(driver_id, filters.weekDate)
    if(driver is None):
        response.status_code = 404
        return {"error": "Driver not found"}
    return driver.schedules

