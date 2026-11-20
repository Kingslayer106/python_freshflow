import numpy as np
import pytest

from freshflow.loader import COLUMNS, load_sales, save_array


def write_csv(path, rows):
    with open(path, "w") as file:
        file.write(",".join(COLUMNS) + "\n")
        for row in rows:
            file.write(row + "\n")


def test_blank_cell_becomes_nan(tmp_path):
    path = tmp_path / "small.csv"
    write_csv(path, ["1,2,1,1,1,1,50,20,0.1,10,1,"])
    data = load_sales(path, expected_rows=1)
    assert data.shape == (1, 12)
    assert np.isnan(data[0, 11])


def test_single_row_stays_two_dimensional(tmp_path):
    path = tmp_path / "single.csv"
    write_csv(path, ["1,2,1,1,1,1,50,20,0.1,10,1,4"])
    assert load_sales(path, expected_rows=1).ndim == 2


def test_wrong_row_count_raises_assertion(tmp_path):
    path = tmp_path / "short.csv"
    write_csv(path, ["1,2,1,1,1,1,50,20,0.1,10,1,4"])
    with pytest.raises(AssertionError):
        load_sales(path)


def test_expected_rows_none_skips_the_row_check(tmp_path):
    path = tmp_path / "clean.csv"
    write_csv(path, ["1,2,1,1,1,1,50,20,0.1,10,1,4", "2,3,1,1,1,2,50,20,0.1,10,1,4"])
    assert load_sales(path, expected_rows=None).shape == (2, 12)


def test_missing_file_raises_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_sales(tmp_path / "nothing.csv")


def test_wrong_header_raises_error(tmp_path):
    path = tmp_path / "bad_header.csv"
    with open(path, "w") as file:
        file.write("a,b,c\n1,2,3\n")
    with pytest.raises(ValueError):
        load_sales(path, expected_rows=1)


def test_save_and_load_round_trip(tmp_path):
    data = np.array([[1, 2, 1, 1, 1, 1, 50.5, 20.25, 0.1, 10, 1, np.nan]], dtype=float)
    path = tmp_path / "round_trip.csv"
    save_array(path, data)
    np.testing.assert_array_equal(load_sales(path, expected_rows=1), data)