import pandas as pd
from django.core.files.base import ContentFile
from typing import Dict, List, Tuple, Optional
import requests
import base64
import re

from monitoring.models import Object, ObjectCategory


def import_objects_from_excel(excel_file, created_by_user, organization_id) -> Dict:
    """
    Excel fayldan barcha kategoriyalar uchun Object larni import qilish
    """
    try:
        xl_file = pd.ExcelFile(excel_file)
        available_sheets = xl_file.sheet_names

        categories = ObjectCategory.objects.all()

        results = []
        total_created = 0
        total_errors = 0
        categories_processed = 0
        categories_skipped = 0

        for category in categories:
            if not category.name_uz:
                categories_skipped += 1
                continue

            result = _import_for_category(
                category=category,
                excel_file=excel_file,
                available_sheets=available_sheets,
                created_by_user=created_by_user,
                organization_id=organization_id
            )

            if result['processed']:
                results.append(result)
                total_created += result['created_count']
                total_errors += result['errors_count']
                categories_processed += 1
            else:
                categories_skipped += 1

        return {
            'success': True,
            'total_created': total_created,
            'total_errors': total_errors,
            'categories_processed': categories_processed,
            'categories_skipped': categories_skipped,
            'available_sheets': available_sheets,
            'results': results
        }

    except Exception as e:
        return {
            'success': False,
            'error': f'Umumiy xato: {str(e)}',
            'total_created': 0,
            'total_errors': 0,
            'categories_processed': 0,
            'categories_skipped': 0,
            'available_sheets': [],
            'results': []
        }


def _import_for_category(category, excel_file, available_sheets, created_by_user, organization_id=None) -> Dict:
    """
    Bitta kategoriya uchun import
    """
    result = {
        'category_id': category.id,
        'category_name_uz': category.name_uz,
        'processed': False,
        'created_count': 0,
        'created_ids': [],
        'errors_count': 0,
        'errors': []
    }

    try:
        if category.name_uz not in available_sheets:
            return result

        df = _read_sheet_data(excel_file, category.name_uz)

        if df.empty:
            return result

        created_ids, errors = _create_objects_from_dataframe(
            df=df,
            category=category,
            created_by_user=created_by_user,
            organization_id=organization_id
        )

        result.update({
            'processed': True,
            'created_count': len(created_ids),
            'updated_or_created_ids': created_ids,
            'errors_count': len(errors),
            'errors': errors
        })

    except Exception as e:
        result.update({
            'processed': True,
            'errors_count': 1,
            'errors': [{
                'error': f"Kategoriya qayta ishlashda xato: {str(e)}"
            }]
        })

    return result


def _read_sheet_data(excel_file, sheet_name: str) -> pd.DataFrame:
    """
    Sheet dan ma'lumotlarni o'qish
    """
    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=1)

    df = df.dropna(how='all')

    return df


def _create_objects_from_dataframe(df, category, created_by_user, organization_id=None) -> Tuple[List[int], List[Dict]]:
    """
    DataFrame dan Object lar yaratish
    """
    created_ids = []
    errors = []

    for index, row in df.iterrows():
        try:
            coordinate_x, coordinate_y = _parse_coordinates(
                row.get('Локацияси', '')
            )

            full_name = _clean_string(row.get('Раҳбар Ф.И.Ш ', ''))

            obj_data = {
                'category': category,
                'phone_number': _clean_string(
                    row.get('Телефон рақами ', '')
                ),
                'address': _clean_string(
                    row.get('Объект юридик манзили ', '')
                ),
                'coordinate_x': coordinate_x,
                'coordinate_y': coordinate_y,
            }

            obj, created = Object.objects.update_or_create(
                organization_id=organization_id,
                full_name=full_name,
                defaults={**obj_data, 'created_by': created_by_user}
            )
            created_ids.append(obj.id)

            image_data = row.get('Расм')
            if pd.notna(image_data) and image_data:
                _process_image(obj, image_data, index)

        except Exception as e:
            errors.append({
                'row': index + 2,  # Excel da header 2-qatorda
                'error': str(e),
                'data': {
                    'full_name': _clean_string(row.get('Раҳбар Ф.И.Ш ', '')),
                    'phone_number': _clean_string(row.get('Телефон рақами ', '')),
                }
            })

    return created_ids, errors


def _clean_string(value) -> str:
    if pd.isna(value):
        return ''
    return str(value).strip()


def _parse_coordinates(location_str) -> Tuple[Optional[str], Optional[str]]:
    if pd.isna(location_str) or not location_str:
        return None, None

    try:
        location_str = str(location_str).strip()

        parts = location_str.split(',', 1)
        if len(parts) == 2:
            coordinate_x = parts[0].strip()
            coordinate_y = parts[1].strip().replace(',', '.')
            return coordinate_x, coordinate_y

    except Exception as e:
        print(f"Koordinata parse xatosi '{location_str}': {e}")

    return None, None


def _process_image(obj, image_data, row_index: int):
    print(image_data, row_index)
    try:
        if isinstance(image_data, str) and (
                image_data.startswith('http://') or
                image_data.startswith('https://')
        ):
            response = requests.get(image_data, timeout=10)
            if response.status_code == 200:
                image_content = ContentFile(response.content)
                obj.avatar.save(
                    f'avatar_{obj.id}.jpg',
                    image_content,
                    save=True
                )

        elif isinstance(image_data, str) and 'base64' in image_data:
            format_match = re.search(r'data:image/(\w+);base64,', image_data)
            if format_match:
                image_format = format_match.group(1)
                base64_data = image_data.split('base64,')[1]
                image_content = ContentFile(base64.b64decode(base64_data))
                obj.avatar.save(
                    f'avatar_{obj.id}.{image_format}',
                    image_content,
                    save=True
                )

    except Exception as e:
        print(f"Rasm yuklash xatosi (row {row_index}): {e}")
