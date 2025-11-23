from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List, cast

from database import get_db
from models import Contact, User
from schemas import ContactCreate, ContactUpdate, ContactResponse
from auth import get_current_user

router = APIRouter(prefix="/contacts", tags=["Contacts"])


def _filter_by_user(query, current_user: User):
    return query.filter(Contact.user_id == current_user.id)


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    contact: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # ЗАЩИТА
):
    db_contact = (
        db.query(Contact)
        .filter(Contact.email == contact.email, Contact.user_id == current_user.id)
        .first()
    )

    if db_contact:
        raise HTTPException(
            status_code=400,
            detail="Contact with this email already exists for this user",
        )

    db_contact = Contact(**contact.model_dump(), user_id=current_user.id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


@router.get("/", response_model=List[ContactResponse])
def read_contacts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # ЗАЩИТА
):
    query = db.query(Contact)
    contacts = _filter_by_user(query, current_user).offset(skip).limit(limit).all()
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
def read_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # ЗАЩИТА
):
    contact = (
        _filter_by_user(db.query(Contact), current_user)
        .filter(Contact.id == contact_id)
        .first()
    )
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: int,
    contact: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # ЗАЩИТА
):
    db_contact = (
        _filter_by_user(db.query(Contact), current_user)
        .filter(Contact.id == contact_id)
        .first()
    )
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    for key, value in contact.model_dump(exclude_unset=True).items():
        setattr(db_contact, key, value)

    db.commit()
    db.refresh(db_contact)
    return db_contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_contact = (
        _filter_by_user(db.query(Contact), current_user)
        .filter(Contact.id == contact_id)
        .first()
    )
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(db_contact)
    db.commit()
    return None


@router.get("/search/", response_model=List[ContactResponse])
def search_contacts(
    query: str = Query(
        ..., min_length=3, description="Пошук за іменем, прізвищем чи email"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # ЗАЩИТА
):
    base_query = _filter_by_user(db.query(Contact), current_user)

    contacts = base_query.filter(
        (Contact.first_name.ilike(f"%{query}%"))
        | (Contact.last_name.ilike(f"%{query}%"))
        | (Contact.email.ilike(f"%{query}%"))
    ).all()

    if not contacts:
        raise HTTPException(
            status_code=404, detail="No contacts found matching the query"
        )

    return contacts


def _check_birthday(contact_date: date, today: date, in_7_days: date) -> bool:
    if contact_date is None:
        return False

    birthday_this_year = contact_date.replace(year=today.year)

    if birthday_this_year < today:
        birthday_this_year = birthday_this_year.replace(year=today.year + 1)

    return today <= birthday_this_year <= in_7_days


@router.get("/birthdays/", response_model=List[ContactResponse])
def get_upcoming_birthdays(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    in_7_days = today + timedelta(days=7)

    all_contacts = _filter_by_user(db.query(Contact), current_user).all()

    upcoming_birthdays = [
        contact
        for contact in all_contacts
        if _check_birthday(cast(date, contact.birthday), today, in_7_days)
    ]

    return upcoming_birthdays
