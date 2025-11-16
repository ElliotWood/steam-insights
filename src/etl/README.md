# ETL Scripts

This folder contains Extract-Transform-Load scripts for importing data into the Steam Insights database.

## Structure

```
src/etl/
├── zenodo/          # Zenodo dataset import scripts
│   ├── import_tag_associations.py
│   └── import_release_dates.py
└── game_importer.py # Steam API game importer
```

## Zenodo Import Scripts

Located in `src/etl/zenodo/`. These scripts import data from the Zenodo Steam Dataset (2025).

### Prerequisites

1. Download Zenodo dataset to `data/zenodo_analysis/csv_data/steam_dataset_2025_csv/`
2. Ensure PostgreSQL database is running
3. Configure `DATABASE_URL` in `.env` or environment

### Usage

**Import Release Dates** (5-10 minutes):
```bash
python src/etl/zenodo/import_release_dates.py
```
- Imports release dates from `applications.csv`
- Updates games that don't have dates yet
- Expected: 80%+ coverage

**Import Tag Associations** (10-15 minutes):
```bash
python src/etl/zenodo/import_tag_associations.py
```
- Imports category/tag associations from `application_categories.csv`
- Uses **name-based matching** (not ID matching)
- Maps Zenodo category IDs → names → database tag IDs
- Expected: 90%+ coverage

### How It Works

#### Name-Based Matching

The Zenodo dataset uses different IDs than our database:
- **Zenodo**: 462 category IDs (multilingual, e.g., "Multiplayer" in 15 languages)
- **Database**: 80 unique English category names with sequential IDs

The import scripts:
1. Load Zenodo categories with their IDs and names
2. Match Zenodo category names to database tag names (case-insensitive)
3. Create mapping: `Zenodo category_id → database tag_id`
4. Import associations using the mapped IDs

#### Example Mapping

```
Zenodo ID 4 "Multiplayer" → Database Tag ID 1 "Multi-player"
Zenodo ID 19 "Steam Sıralama Listeleri" → No match (Turkish)
```

### Data Quality

**Matched Categories**: ~81 out of 462
- English categories match well
- Non-English categories (381) are duplicates in other languages

**Expected Results**:
- Release Dates: 80-85% coverage (179K+ games)
- Tag Associations: 90%+ coverage (190K+ games)

### Troubleshooting

**"No valid associations to import"**
- Check if category names in Zenodo match tag names in database
- Verify tags exist: `SELECT name FROM tags WHERE is_user_tag = false;`

**"Duplicate key violation"**
- Normal - script handles duplicates by skipping them
- Existing associations are preserved

**"Database connection failed"**
- Check `DATABASE_URL` in environment
- Verify PostgreSQL is running

## Future Imports

When new Zenodo datasets are released:
1. Download new CSV files to `data/zenodo_analysis/csv_data/`
2. Run import scripts in order:
   - Release dates first (faster, independent)
   - Tag associations second (slower, 10-15 mins)
3. Verify coverage with dashboard or SQL queries

## Performance

- **Release Dates**: ~5 minutes for 180K updates
- **Tag Associations**: ~10-15 minutes for 800K+ inserts
- Uses batch processing (1000-5000 records per batch)
- Progress updates every 50K records
