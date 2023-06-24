from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.loans import LoanSchemaBase, LoanSchema, LoanScheduleSchema, Loan, LoanAccess


class LoanController:
    
    @staticmethod
    def validateLoan(loan: LoanSchemaBase):
        '''
        Validate the input data for loan creation
        Returns:
            HTTPException if validation fails
            None otherwise
        '''
        if not isinstance(loan.amount, float):
            return HTTPException(status_code=400, detail="Loan amount must be a float" )
        if loan.amount <= 0:
            return HTTPException(status_code=400, detail="Loan amount must be greater than zero" )
        if not isinstance(loan.apr, float):
            return HTTPException(status_code=400, detail="Loan interest_rate must be a float" )
        if loan.apr <= 0:
            return HTTPException(status_code=400, detail="Loan interest_rate must be greater than zero" )
        if not isinstance(loan.term, int):
            return HTTPException(status_code=400, detail="Loan term must be an int (number of months)" )
        if loan.term <= 0:
            return HTTPException(status_code=400, detail="Loan term must be greater than zero" )
        if not isinstance(loan.status, str):
            return HTTPException(status_code=400, detail="Loan status must be a string" )
        if loan.status not in ["active", "inactive"]:
            return HTTPException(status_code=400, detail="Loan status must be either 'active' or 'inactive'" )
        if not isinstance(loan.owner_id, int):
            return HTTPException(status_code=400, detail="Loan owner_id must be an int" )
        else:
            return None

    @staticmethod
    def create_loan(db: Session, loanData: LoanSchemaBase):
        loan = Loan(**loanData.dict())
        db.add(loan)
        db.commit()
        db.refresh(loan)
        return loan

    @staticmethod
    def get_loan_by_id(db: Session, id: int):
        return db.query(Loan).filter(Loan.id == id).first()

    @staticmethod
    def get_loans_by_owner_id(db: Session, owner_id: int, skip: int=0, limit: int=100):
        return db.query(Loan).filter(Loan.owner_id == owner_id).offset(skip).limit(limit).all()

    @staticmethod
    def update_loan(db: Session, loan: Loan, loanData: LoanSchemaBase):
        
        for k,v in loanData.__dict__.items():
            setattr(loan, k, v)

        db.commit()
        db.refresh(loan)
        return loan
    
    @staticmethod
    def calc_monthly_total_payment(apr: float, balance: float, term: int):
        temp_val = ((apr / 12) + 1) ** term
        return balance * ((apr / 12 * temp_val) / (temp_val - 1))

    @staticmethod
    def calc_monthly_interest(apr: float, balance: float):
        return balance * apr / 12

    @staticmethod
    def calc_monthly_principal_payment(apr: float, balance: float, term: int):
        return LoanController.calc_monthly_total_payment(apr, balance, term) - LoanController.calc_monthly_interest(apr, balance)

    @staticmethod
    def get_loan_schedule_for_loan(loan: LoanSchema):
        return LoanController.get_loan_schedule(loan.apr, loan.amount, loan.term)

    @staticmethod
    def get_loan_schedule(apr: float, amount: float, term: int):
        schedule = []
        monthly_payment = LoanController.calc_monthly_total_payment(apr, amount, term)
        principal = amount

        for month in range(1, term + 1):

            interest_amount = LoanController.calc_monthly_interest(apr, principal)
            principal_payment = monthly_payment - interest_amount

            open_balance = principal
            principal -= principal_payment
            close_balance = principal

            schedule.append(LoanScheduleSchema(
                month=month, open_balance=open_balance, close_balance=close_balance, total_payment=monthly_payment,
                principal_payment=principal_payment, interest_payment=interest_amount)
            )

        return schedule

    @staticmethod
    def get_loan_summary_for_loan(loan: LoanSchema, month: int):
        return LoanController.get_loan_summary(loan.apr, loan.amount, loan.term, month)

    @staticmethod
    def get_loan_summary(apr: float, amount: float, term: int, month: int):
        """
        Generates a summary of the loan for the given month.
        Month 0 is the initial state of the loan, Month 1 is after the first payment.
        """
        total_interest = 0
        total_principal = 0
        current_principal = amount

        if month < 0:
            raise ValueError("Month must be greater than or equal to zero")
        if month > term:
            raise ValueError("Month must be less than or equal to the loan term")
        if month > 0:
            schedule = LoanController.get_loan_schedule(apr, amount, term)
            for i in range (0, month):
                total_interest += schedule[i].interest_payment
                total_principal += schedule[i].principal_payment
                current_principal = schedule[i].close_balance
        return {
            "current_principal": current_principal,
            "aggregate_principal_paid": total_principal,
            "aggregate_interest_paid": total_interest
        }
    
    @staticmethod
    def access_check(db: Session, loan_id: int, user_id: int):
        '''
        Check if a user has access to a loan
        Returns True/False
        '''
        return db.query(LoanAccess).filter(LoanAccess.loan_id == loan_id, LoanAccess.user_id == user_id).first() is not None

    @staticmethod
    def add_user(db: Session, loan_id: int, user_id: int):
        '''
        Add access for the user to view the loan
        '''
        # succeed fast if the user already has access
        if LoanController.access_check(db, loan_id, user_id):
            return True

        db_loan_access = LoanAccess(loan_id=loan_id, user_id=user_id)
        db.add(db_loan_access)
        db.commit()
        db.refresh(db_loan_access)
        return True

    @staticmethod
    def get_loans_by_user_id(db: Session, user_id: int):
        '''
        Get a list of all loans a user has access to
        '''
        return db.query(Loan).join(LoanAccess, LoanAccess.loan_id == Loan.id).filter(LoanAccess.user_id == user_id).all()