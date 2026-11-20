import numpy as np

from freshflow.loader import COL
from freshflow.validation import column, duplicate_id_mask, invalid_masks

POLICY = {
    "duplicate transaction_id": ("keep", "same ID but other fields differ, so these are different sales"),
    "exact duplicate copy": ("exclude", "identical row repeated, only the first copy is kept"),
    "invalid transaction_id": ("exclude", "ID is missing, non-positive or not a whole number"),
    "invalid day": ("exclude", "day is outside 1-30"),
    "unknown outlet": ("exclude", "outlet code is not 1, 2 or 3"),
    "unknown product": ("exclude", "product code is not 1-8"),
    "unknown payment": ("exclude", "payment code is not 1-4"),
    "category mismatch": ("exclude", "category does not match product, correct one is unknown"),
    "quantity not positive": ("exclude", "zero or negative quantity is not a completed sale"),
    "quantity not whole": ("exclude", "units sold must be a whole number"),
    "price not positive": ("exclude", "price must be greater than zero"),
    "negative unit cost": ("exclude", "cost cannot be negative"),
    "discount outside 0-1": ("exclude", "discount rate is impossible"),
    "negative stock": ("exclude", "stock cannot be negative"),
    "infinite value": ("exclude", "infinite number in the row"),
    "invalid rating": ("make_nan", "rating is outside 1-5, set to NaN and the sale is kept"),
}

EXCLUDE_RULES = [rule for rule, (action, _) in POLICY.items() if action == "exclude"]


def exact_copy_mask(data):
    flagged = np.nonzero(duplicate_id_mask(column(data, "transaction_id")))[0]
    copies = np.zeros(len(data), dtype=bool)
    if len(flagged) == 0:
        return copies
    _, first_positions = np.unique(data[flagged], axis=0, return_index=True)
    copies[np.delete(flagged, first_positions)] = True
    return copies


def build_masks(data):
    masks = invalid_masks(data)
    masks["exact duplicate copy"] = exact_copy_mask(data)
    return masks


def exclusion_mask(masks):
    return np.vstack([masks[rule] for rule in EXCLUDE_RULES]).any(axis=0)


def reason_codes(masks):
    table = np.vstack([masks[rule] for rule in EXCLUDE_RULES])
    return table.argmax(axis=0) + 1


def clean_data(data):
    masks = build_masks(data)
    exclude = exclusion_mask(masks)

    clean = data[~exclude].copy()
    rating = clean[:, COL["customer_rating"]]
    rating[masks["invalid rating"][~exclude]] = np.nan

    excluded = np.column_stack((data[exclude], reason_codes(masks)[exclude]))
    return clean, excluded, masks, exclude


def cleaning_report(masks, exclude):
    lines = []
    for rule, (action, reason) in POLICY.items():
        flagged = int(masks[rule].sum())
        removed = int((masks[rule] & exclude).sum())
        lines.append(f"{rule} | flagged={flagged} | excluded={removed} | action={action} | {reason}")
    return lines


def write_cleaning_report(path, masks, exclude, raw_rows):
    lines = cleaning_report(masks, exclude)
    with open(path, "w") as file:
        file.write(f"Raw rows: {raw_rows}\n")
        file.write(f"Excluded rows: {int(exclude.sum())}\n")
        file.write(f"Clean rows: {raw_rows - int(exclude.sum())}\n\n")
        file.write("\n".join(lines))
        file.write("\n\nExcluded file: last column reason_code is the position (starting at 1) of the first rule below.\n")
        for number, rule in enumerate(EXCLUDE_RULES, start=1):
            file.write(f"{number} = {rule}\n")