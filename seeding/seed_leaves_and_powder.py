import random
from sqlalchemy.orm import Session
import models
from datetime import datetime, timedelta
from database import get_db

def seed_leaves_and_powder(db: Session, num_centras: int = 5, num_each: int = 10):
    # Get random centras (users with RoleID == 1)
    centras = db.query(models.User).filter(models.User.RoleID == 1).all()
    if not centras:
        print("No centras found!")
        return
    centras = random.sample(centras, min(num_centras, len(centras)))

    for centra in centras:
        for _ in range(num_each):
            # Wet Leaves
            wet = models.WetLeaves(
                UserID=centra.UserID,
                Weight=random.uniform(10, 100),
                Expiration=datetime.now() + timedelta(days=random.randint(1, 10)),
                Status="awaiting",
                ReceivedTime=datetime.now()
            )
            db.add(wet)
            db.commit()
            db.refresh(wet)

            # Dry Leaves
            dry = models.DryLeaves(
                UserID=centra.UserID,
                WetLeavesID=wet.WetLeavesID,
                Processed_Weight=wet.Weight * random.uniform(0.5, 0.9),
                Expiration=wet.Expiration + timedelta(days=random.randint(1, 5)),
                Status="awaiting"
            )
            db.add(dry)
            db.commit()
            db.refresh(dry)

            # Flour (Powder)
            flour = models.Flour(
                UserID=centra.UserID,
                DryLeavesID=dry.DryLeavesID,
                Flour_Weight=dry.Processed_Weight * random.uniform(0.5, 0.9),
                Expiration=dry.Expiration + timedelta(days=random.randint(1, 5)),
                Status="awaiting"
            )
            db.add(flour)
            db.commit()
    print(f"Seeded {num_each} wet, dry, and powder leaves for {len(centras)} centras.")

if __name__ == "__main__":
    db = get_db()
    seed_leaves_and_powder(db)
    db.close()