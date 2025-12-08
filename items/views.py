from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as django_login
from django.conf import settings
from .models import LostItem, Message
from .serializers import LostItemSerializer, MessageSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.generics import ListCreateAPIView
from django.db.models import Max
@api_view(['GET'])
@permission_classes([AllowAny])
def health_superuser(request):
    """Report whether the configured superuser exists and is staff.

    Returns JSON: {"exists": bool, "is_staff": bool, "username": str}
    """
    username = os.getenv('DJANGO_SUPERUSER_USERNAME') or 'admin'
    try:
        user = User.objects.filter(username=username).first()
        if not user:
            return Response({"exists": False, "is_staff": False, "username": username})
        return Response({"exists": True, "is_staff": bool(user.is_staff), "username": user.username})
    except Exception as e:
        return Response({"error": str(e)}, status=500)

class LostItemListCreateView(generics.ListCreateAPIView):
    queryset = LostItem.objects.order_by('-created_at')
    serializer_class = LostItemSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class LostItemDetailView(generics.RetrieveUpdateAPIView):
    queryset = LostItem.objects.all()
    serializer_class = LostItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Only allow staff (admin) to modify claimed status
        if not request.user.is_staff:
            return Response({'detail': 'Admin required to update claimed status.'}, status=403)
        # Allow admin to update 'claimed' and 'found' flags via the same endpoint.
        updated = False
        claimed_value = request.data.get('claimed')
        if claimed_value is not None:
            if claimed_value in [True, 'true', 'True', '1', 1]:
                instance.claimed = True
                updated = True
            elif claimed_value in [False, 'false', 'False', '0', 0]:
                instance.claimed = False
                updated = True
            else:
                return Response({'claimed': ['Invalid value']}, status=400)
        found_value = request.data.get('found')
        if found_value is not None:
            if found_value in [True, 'true', 'True', '1', 1]:
                instance.found = True
                updated = True
            elif found_value in [False, 'false', 'False', '0', 0]:
                instance.found = False
                updated = True
            else:
                return Response({'found': ['Invalid value']}, status=400)
        if not updated:
            return Response({'detail': 'No updatable fields provided. Provide `claimed` and/or `found`.'}, status=400)
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    # Defensive parsing + trimming to give clearer errors when clients send unexpected payloads
    try:
        username = (request.data.get('username') or '').strip()
        password = request.data.get('password') or ''
        full_name = request.data.get('full_name')
        gender = request.data.get('gender')
    except Exception as e:
        # If request.data is not a mapping, include a hint for debugging
        return Response({'detail': 'Unable to parse request data', 'error': str(e)}, status=400)

    if not username or not password:
        # Return which keys were present to help the client debug
        received = list(request.data.keys()) if hasattr(request.data, 'keys') else []
        return Response({'detail': 'Username and password required.', 'received_keys': received}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({'detail': 'Username already taken.'}, status=400)
    user = User.objects.create_user(username=username, password=password)
    # If the registering username is the special Admin name, mark as staff
    if username == 'Admin':
        user.is_staff = True
        user.save()
    # Create or update a Profile for storing additional user info
    try:
        from .models import Profile
        # Set user's built-in name/email fields when provided
        if full_name:
            # If full_name was provided (older clients), try to split into first/last
            parts = (full_name or '').strip().split(None, 1)
            if parts:
                user.first_name = parts[0]
                if len(parts) > 1:
                    user.last_name = parts[1]
        # New fields: first_name, last_name, email may have been provided
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if email:
            user.email = email
        user.save()
        Profile.objects.create(user=user, first_name=(first_name or user.first_name or ''), last_name=(last_name or user.last_name or ''), email=(email or user.email or ''), gender=(gender or 'unspecified'))
    except Exception:
        # If migrations haven't been run or Profile cannot be created, ignore to keep registration working
        pass
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'is_admin': user.is_staff, 'user': {'id': user.id, 'username': user.username, 'first_name': user.first_name, 'last_name': user.last_name}})


class MessageListCreateView(ListCreateAPIView):
    """List messages and allow creating new messages.

    - Authenticated regular users post messages attached to their account (sender='user').
    - Authenticated staff users post messages with sender='admin' and must specify a `user` id to reply to.
    - GET: staff can filter `?user=<id>` to see a user's conversation; regular users only see their own conversation.
    """
    queryset = Message.objects.order_by('created_at')
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = super().get_queryset()
        user_param = self.request.query_params.get('user')
        # If staff and user filter provided, return that conversation
        if self.request.user and self.request.user.is_authenticated and self.request.user.is_staff:
            if user_param:
                return qs.filter(user__id=user_param)
            # else return all messages (or we could return conversations list)
            return qs
        # Non-staff users should only see their conversation
        if self.request.user and self.request.user.is_authenticated:
            return qs.filter(user=self.request.user)
        # Unauthenticated: no messages
        return Message.objects.none()

    def perform_create(self, serializer):
        if not (self.request.user and self.request.user.is_authenticated):
            raise Response({'detail': 'Authentication required to post messages.'}, status=403)
        # Attachments are no longer supported in chat; ignore any uploaded files
        if self.request.user.is_staff:
            # Admin must specify a user id to reply to
            user_obj = None
            user_id = self.request.data.get('user')
            if not user_id:
                raise Response({'user': ['This field is required for admin replies.']}, status=400)
            try:
                user_obj = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return Response({'user': ['User not found.']}, status=400)
            serializer.save(sender='admin', user=user_obj)
        else:
            # Regular user: attach to their account
            serializer.save(sender='user', user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Override to ensure response uses serializer with request context so file fields
        # (attachment) are rendered as full URLs and clients can fetch them.
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Use perform_create to apply our save logic
        self.perform_create(serializer)
        # serializer.save() doesn't return the instance here; get the instance from DB by latest created message for this user/sender
        # However, since perform_create used serializer.save, DRF has set serializer.instance. Use that when available.
        instance = getattr(serializer, 'instance', None)
        if instance is None:
            # as a fallback, try to fetch the latest message for this user
            if request.user and request.user.is_authenticated:
                instance = Message.objects.filter(user=request.user).order_by('-created_at').first()
            else:
                instance = Message.objects.order_by('-created_at').first()
        headers = self.get_success_headers(serializer.data)
        # Return serialized instance with request context so attachment URL is absolute
        return Response(MessageSerializer(instance, context={'request': request}).data, status=201, headers=headers)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    """Simple fixed-credentials admin login.

    If username == 'Admin' and password == 'Admin123', ensure a staff user exists
    with username 'Admin' and return the auth token. This allows the front-end
    to perform admin actions using the returned token.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    if username == 'Admin' and password == 'Admin123':
        user, created = User.objects.get_or_create(username='Admin')
        # Ensure the user is staff so permission checks work
        if not user.is_staff:
            user.is_staff = True
        # Ensure password is set to the fixed one so authenticate() works if used elsewhere
        user.set_password('Admin123')
        user.save()
        # Create auth token for API usage
        token, _ = Token.objects.get_or_create(user=user)
        # Also create a Django session so browser clients that rely on cookies remain logged-in across reloads
        try:
            django_login(request, user)
        except Exception:
            # If sessions aren't configured or login fails for any reason, ignore and continue returning token
            pass
        payload = {'token': token.key, 'is_admin': user.is_staff, 'user': {'id': user.id, 'username': user.username, 'first_name': user.first_name, 'last_name': user.last_name}}
        resp = Response(payload)
        # Cookie attributes: when running in production (DEBUG=False) browsers require
        # SameSite=None and Secure=True for cross-site cookies. For local development
        # we keep SameSite=Lax and Secure=False so cookies work over HTTP on localhost.
        samesite = 'Lax' if settings.DEBUG else 'None'
        secure = False if settings.DEBUG else True
        try:
            resp.set_cookie('authToken', token.key, max_age=30*24*3600, httponly=False, samesite=samesite, secure=secure)
        except Exception:
            pass
        return resp
    return Response({'detail': 'Invalid admin credentials'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    try:
        username = (request.data.get('username') or '').strip()
        password = request.data.get('password') or ''
    except Exception as e:
        return Response({'detail': 'Unable to parse request data', 'error': str(e)}, status=400)

    if not username or not password:
        received = list(request.data.keys()) if hasattr(request.data, 'keys') else []
        return Response({'detail': 'Username and password required.', 'received_keys': received}, status=400)

    user = authenticate(username=username, password=password)
    if not user:
        return Response({'detail': 'Invalid credentials'}, status=400)
    token, _ = Token.objects.get_or_create(user=user)
    payload = {'token': token.key, 'is_admin': user.is_staff, 'user': {'id': user.id, 'username': user.username, 'first_name': user.first_name, 'last_name': user.last_name}}
    resp = Response(payload)
    samesite = 'Lax' if settings.DEBUG else 'None'
    secure = False if settings.DEBUG else True
    try:
        resp.set_cookie('authToken', token.key, max_age=30*24*3600, httponly=False, samesite=samesite, secure=secure)
    except Exception:
        pass
    return resp


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def whoami(request):
    """Return the currently authenticated user (via session or token).

    This helps debugging whether session or token auth is active after a page reload.
    """
    user = request.user
    if user and user.is_authenticated:
        return Response({'authenticated': True, 'user': {'id': user.id, 'username': user.username, 'first_name': user.first_name, 'last_name': user.last_name}})
    return Response({'authenticated': False})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def conversations(request):
    """Return a list of conversations (per-user) with last message and unread count.

    Only staff users should call this endpoint; non-staff will get a 403.
    Unread count is approximated as the number of user-sent messages after the latest admin message.
    """
    # Allow admin authentication via token cookie (authToken) for browser clients that rely on cookies
    if not request.user.is_authenticated:
        token_key = request.COOKIES.get('authToken') or request.data.get('authToken') if hasattr(request, 'data') else None
        if token_key:
            try:
                token_obj = Token.objects.get(key=token_key)
                request.user = token_obj.user
            except Token.DoesNotExist:
                pass

    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({'detail': 'Admin credentials required.'}, status=403)
    # Gather users who have messages
    user_ids = Message.objects.filter(user__isnull=False).values_list('user', flat=True).distinct()
    results = []
    for uid in user_ids:
        try:
            user_obj = User.objects.get(pk=uid)
        except User.DoesNotExist:
            continue
        last_msg = Message.objects.filter(user__id=uid).order_by('-created_at').first()
        last_admin_time = Message.objects.filter(user__id=uid, sender='admin').aggregate(latest=Max('created_at'))['latest']
        if last_admin_time:
            unread_count = Message.objects.filter(user__id=uid, sender='user', created_at__gt=last_admin_time).count()
        else:
            unread_count = Message.objects.filter(user__id=uid, sender='user').count()
        results.append({
            'user': uid,
            'user_name': user_obj.username,
            'user_display': f"{(user_obj.first_name or '').strip()} {(user_obj.last_name or '').strip()}".strip() or user_obj.username,
            'last_message': last_msg.text if last_msg else '',
            'last_message_time': last_msg.created_at if last_msg else None,
            'unread_count': unread_count,
        })
    # sort by last_message_time desc
    results.sort(key=lambda x: x['last_message_time'] or '', reverse=True)
    # Convert datetimes to ISO strings for JSON serialization
    for r in results:
        if r['last_message_time']:
            r['last_message_time'] = r['last_message_time'].isoformat()
    return Response(results)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def contact_admin(request):
    """Allow a regular authenticated user to send a message directed to admin(s).

    The message will be saved with sender='user' and user=request.user so admins
    can view the conversation by filtering messages by the user's id.
    """
    if request.user.is_staff:
        return Response({'detail': 'Admins should use the admin reply endpoints.'}, status=400)
    serializer = MessageSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    # Save message attached to the sending user
    # Attachments are no longer supported in chat; ignore any uploaded files
    msg = serializer.save(sender='user', user=request.user)
    return Response(MessageSerializer(msg, context={'request': request}).data, status=201)
