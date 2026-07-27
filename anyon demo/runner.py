
from QuantumMath.HilbertSpace import hilbertSpace

from anyons.AnyonOperation import AnyonOperation
from anyons.FusionSystem import FusionSystem



def test_operation_history():
    system = FusionSystem(2)

    # יצירת פעולת R
    r_operation = AnyonOperation(
        operation_type="R",
        first_id=1,
        second_id=2
    )

    # יצירת פעולת F הפוכה
    f_operation = AnyonOperation(
        operation_type="F",
        inverse=True,
        path=(0,),
        direction="left"
    )

    # בדיקת תוכן האובייקטים
    assert r_operation.operation_type == "R"
    assert r_operation.inverse is False
    assert r_operation.parameters["first_id"] == 1
    assert r_operation.parameters["second_id"] == 2

    assert f_operation.operation_type == "F"
    assert f_operation.inverse is True
    assert f_operation.parameters["path"] == (0,)
    assert f_operation.parameters["direction"] == "left"

    # בדיקה שההיסטוריה מתחילה ריקה
    assert system.get_operation_history() == []

    # הוספת פעולות
    system.record_operation(r_operation)
    system.record_operation(f_operation)

    history = system.get_operation_history()

    # בדיקת מספר הפעולות והסדר שלהן
    assert len(history) == 2
    assert history[0] is r_operation
    assert history[1] is f_operation

    # בדיקה שהחזרת ההיסטוריה היא עותק של הרשימה
    history.clear()

    assert len(history) == 0
    assert len(system.get_operation_history()) == 2

    # בדיקת ניקוי ההיסטוריה האמיתית
    system.clear_operation_history()

    assert system.get_operation_history() == []

    # בדיקת קלט לא חוקי ל-record_operation
    try:
        system.record_operation("R")
        assert False, "Expected TypeError for invalid operation."
    except TypeError:
        pass

    # בדיקת operation_type לא חוקי
    try:
        AnyonOperation(
            operation_type=5
        )
        assert False, "Expected TypeError for invalid operation_type."
    except TypeError:
        pass

    # בדיקת inverse לא חוקי
    try:
        AnyonOperation(
            operation_type="R",
            inverse="False"
        )
        assert False, "Expected TypeError for invalid inverse."
    except TypeError:
        pass

    print(r_operation)
    print(f_operation)


    print("All operation history tests passed.")


if __name__ == "__main__":
    test_operation_history()