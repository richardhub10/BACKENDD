# Lost & Found Prototype

A basic Facebook-like feed for lost & found items built with:
- **Backend:** Django + Django REST Framework (SQLite, Token Auth)
- **Frontend:** React Native (Expo)

## Features
- List items with image, name, category, date found, description, poster username, claimed status badge
- Tap an item to view a detail page
- Admin can mark items claimed / unclaimed (via Item Detail screen)
- Post new item with image upload (multipart form)
- Auto demo user registration/login (token stored in memory only for prototype)
- CORS open for development

## Backend Setup (Windows PowerShell)
```powershell
cd 
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```
Visit: http://127.0.0.1:8000/api/items/

Admin (optional):
```powershell
python manage.py createsuperuser
```

## Frontend Setup
Install Node.js (LTS) if not already.
```powershell
cd 
npm install
npx expo start
```
Press "a" for Android emulator or scan QR for device (ensure device can reach your PC's IP; replace `127.0.0.1` in `client.js` with your machine LAN IP if using a physical device).

## API Endpoints
- `POST /api/items/register/` { username, password } -> { token }
- `POST /api/items/login/` { username, password } -> { token }
- `GET /api/items/` -> list items
- `POST /api/items/` (Token auth + multipart) fields: name, category, description, date_found, image
- `GET /api/items/<id>/` -> item detail (includes claimed)
- `PATCH /api/items/<id>/` (admin only) body: claimed=true|false

## Media
Uploaded images stored under `backend/media/item_images/`. Served in development via `settings.DEBUG` static route.

## Claimed Status
Run migrations after adding the claimed field:
```powershell
cd 
.\.venv\Scripts\python manage.py makemigrations items
.\.venv\Scripts\python manage.py migrate
```
Create or convert a user to admin/staff (in Django admin or shell) to toggle claimed:
```powershell
.\.venv\Scripts\python manage.py createsuperuser
```
In the mobile app edit `ItemDetailScreen.js` ADMIN_USERNAME / ADMIN_PASSWORD to match your staff account.

## Adjusting for Physical Device
Edit `mobile/src/api/client.js`:
```js
const BASE_URL = 'http://YOUR_PC_LAN_IP:8000';
```
Find LAN IP with:
```powershell
ipconfig | findstr IPv4
```

## Security Notes
- Secret key is hardcoded for development; set `DJANGO_SECRET_KEY` env var for production.
- Token auth in memory only; add persistent/secure storage for real use.

## Next Steps (see NEXT_STEPS.md)
- Filtering, search, pagination
- Persistent auth & logout
- Push notifications for matches
- Moderation workflow

## Troubleshooting
| Issue | Fix |
|-------|-----|
| Image not showing | Use LAN IP instead of 127.0.0.1 on device |
| 403 on POST | Ensure token present; recreate demo user |
| Expo cannot connect | Disable firewall or allow port 19000/8000 |
| Pillow install fails | Ensure Python added to PATH & VS Build Tools installed |

## License
Prototype sample code. Adapt freely.
