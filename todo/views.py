from datetime import datetime
from django.core.mail import send_mail
from nexmomessage import NexmoMessage
from PIL import Image
from rest_framework.parsers import FileUploadParser,JSONParser
from django.core.files import File
from django.shortcuts import get_object_or_404


# Django
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.db.models import Count

# REST Framework
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import DjangoObjectPermissions
from rest_framework.views import APIView
from .permissions import MyUserPermissions

# Provider OAuth2
from provider.oauth2.models import Client

# Todo App
from todo.serializers import RegistrationSerializer
from todo.serializers import UserSerializer, TodoSerializer, GameSerializer,GamesPlayerSerializer , PlayerSerializer, PlayerSerializer2,GameUsersSerializer,GameUsersSerializer2, UserProfileSerializer, GameUsersPutSerializer,ProfileSerializer, GameEmailPutSerializer, ContentSerializer, PhotoSerializer,MyGamesSerializer
from todo.models import Todo, Game, Player, GameUsers, Profile, Content, MyPhoto


def ValuesQuerySetToDict(vqs):
    return [item for item in vqs]

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def send_group_mail(game_id):
    # print "Hello"
    players = GameUsers.objects.filter(game_id=game_id, gstatus="Yes")
   # serializer = PlayerSerializer2(players, many=True)
    serializer = GameUsersSerializer2(players, many=True)
   #     return Response(serializer.data)
    email_list = []
    obj = serializer.data
    for item in obj:
        email_list.append(item['users']['email'])
        #print item['users']['email']
    print email_list 
#    import pdb; pdb.set_trace()
#    send_mail('Subject here', 'ododo', 'slatterytom@gmail.com', ['slatterytom@gmail.com', 'patagucci@yahoo.com'], fail_silently=False)
   # send_mail('Subject here', 'ododo', 'slatterytom@gmail.com', ['slatterytom@gmail.com'], fail_silently=False)

class CurrentUserView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class ResetPasswordConfirm(APIView):
    permission_classes = ()
    parser_classes = (JSONParser, )

    def put(self, request, uidb64, token, format=None):
#        import pdb; pdb.set_trace()
        data = request.DATA
        new_password = data['new_password']   
        uid = urlsafe_base64_decode(uidb64)
        user = User.objects.get(pk=uid)
        token_generator=default_token_generator
        token_check = token_generator.check_token(user,token)
        if (user is not None and token_check): 
        	user.set_password(new_password)
        	user.save()
                return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class ResetPassword(APIView):
    permission_classes = ()
    parser_classes = (JSONParser, )

    def get(self, request, email, format=None):
        user = User.objects.get(username=email)
        token_generator=default_token_generator
        new_token = token_generator.make_token(user)
        uid_64 = urlsafe_base64_encode(force_bytes(user.pk))
        body = "http://localhost:8000/#/passwordreset/" + uid_64 + "/" + new_token  
        print body
     #   import pdb; pdb.set_trace()
        send_mail('Subject here', body, 'slatterytom@gmail.com',[email] , fail_silently=False)
   #     obj = get_object_or_404(User,username=email) 
        return Response(status=status.HTTP_201_CREATED)

class EmailCheckView(APIView):
    permission_classes = (MyUserPermissions,)
    parser_classes = (JSONParser, )

    def get(self, request, email, format=None):
        obj = get_object_or_404(User,username=email) 
        return Response(status=status.HTTP_201_CREATED)

class NickNameCheckView(APIView):
    permission_classes = (MyUserPermissions,)
    parser_classes = (JSONParser, )

    def get(self, request, nickname, format=None):
    #    import pdb; pdb.set_trace()
        obj = get_object_or_404(Profile,nickname=nickname) 
        return Response(status=status.HTTP_201_CREATED)

class UserDetail(APIView):
    permission_classes = (MyUserPermissions,)
    parser_classes = (JSONParser, )

    def get_object(self, pk):
        try:
            obj = User.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj)
            return obj 
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        user = UserSerializer(user)
        #q = UserSerializer(User.objects.get(id=pk).get_profile())
        #import pdb; pdb.set_trace()
        return Response(user.data)

    def put(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.DATA)
#        import pdb; pdb.set_trace()
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
    	#users = User.objects.filter(id=request.user.id)
    	users = User.objects.all()
    	serializer = UserSerializer(users)
    	return Response(serializer.data)


    def put(self, request):
        serializer = UserSerializer(data=request.DATA)
        if not serializer.is_valid():
            return Response(serializer.errors, status=
                status.HTTP_400_BAD_REQUEST)
        else:
            data = serializer.data
            #user = request.user
            #game_id = Game.objects.get(id=data['game_id'])
            fname = data['first_name']
            lname = data['last_name']
            #t = Users(id=request.user.id, user=user, gstatus=gstatus, game_id=game_id)
            t = User(id=request.user.id, first_name=fname, last_name=lname)
            t.save()
            request.DATA['id'] = t.pk # return id
            return Response(request.DATA, status=status.HTTP_201_CREATED)




   # queryset = User.objects.all()
   # serializer_class = UserSerializer


class RegistrationView(APIView):
    """ Allow registration of new users. """
    permission_classes = ()

    def post(self, request):
        serializer = RegistrationSerializer(data=request.DATA)

        # Check format and unique constraint
        if not serializer.is_valid():
            return Response(serializer.errors,\
                            status=status.HTTP_400_BAD_REQUEST)
        data = serializer.data

        u = User.objects.create(username=data['username'])
        u.set_password(data['password'])
        u.save()

        # Create OAuth2 client
        name = u.username
        client = Client(user=u, name=name, url='' + name,\
                client_id=name, client_secret='', client_type=1)
        client.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GamesPlayerView(APIView):
    permission_classes = ()

    def get(self, request, game_id):
        """ Get all todos """
        todos = Player.objects.filter(game=game_id)
       # todos = Player.objects.filter(owner=game_id)
#        import pdb; pdb.set_trace()
        serializer = GamesPlayerSerializer(todos, many=True)
        return Response(serializer.data)

class GamesView(APIView):
    permission_classes = ()

    def get(self, request):
        """ Get all todos """
        todos = Game.objects.all()
        serializer = GameSerializer(todos, many=True)
        return Response(serializer.data)

    def post(self, request):
        """ Adding a new todo. """
        serializer = GameSerializer(data=request.DATA)
        if not serializer.is_valid():
            return Response(serializer.errors, status=
                status.HTTP_400_BAD_REQUEST)
        else:
            data = serializer.data
            #owner = request.user
            t = Game( description=data['description'], done=False)
            t.save()
            request.DATA['id'] = t.pk # return id
            return Response(request.DATA, status=status.HTTP_201_CREATED)

    def put(self, request, todo_id):
        """ Update a todo """
        serializer = TodoSerializer(data=request.DATA)
        if not serializer.is_valid():
            return Response(serializer.errors, status=
                status.HTTP_400_BAD_REQUEST)
        else:
            data = serializer.data
            desc = data['description']
            done = data['done']
            t = Todo(id=todo_id, owner=request.user, description=desc,\
                     done=done, updated=datetime.now())
            t.save()
            return Response(status=status.HTTP_200_OK)

class PlayersView(APIView):
    parser_classes = (JSONParser, )
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """ Get all todos """
        players = Player.objects.filter(owner=request.user.id)
        serializer = PlayerSerializer2(players, many=True)
        return Response(serializer.data)

    def post(self, request):
        """ Adding a new todo. """
        serializer = PlayerSerializer(data=request.DATA)
        if not serializer.is_valid():
            return Response(serializer.errors, status=
                status.HTTP_400_BAD_REQUEST)
        else:
            data = serializer.data
            owner = request.user
            game1 = Game.objects.get(id=data['game'])
            t = Player(owner=owner, game=game1)
            t.save()
            request.DATA['id'] = t.pk # return id
            send_group_mail()
            #send_mail('Subject here', 'Here is the message.', 'slatterytom@gmail.com', ['slatterytom@gmail.com'], fail_silently=False)
            msg = {
		    	'reqtype': 'json',
    	     	    	'api_key': '60215e70',
    			'api_secret': 'a885b16f',
    			'from': '12132633411',
    			'to':'14157865548',
    			'text': 'Hello world!'
			}
            sms = NexmoMessage(msg)
 	    #sms.set_text_info(msg['text'])
            #sms.send_request()
            return Response(request.DATA, status=status.HTTP_201_CREATED)

class UserProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """ Get all todos """
        todos = UserProfile.objects.filter(user=request.user.id)
        #serializer = UserProfileSerializer(todos, many=True)
        serializer = UserProfileSerializer(todos)
        return Response(serializer.data)

    def post(self, request):
        """ Adding a new todo. """
        serializer = UserProfileSerializer(data=request.DATA)
        if not serializer.is_valid():
            return Response(serializer.errors, status=
                status.HTTP_400_BAD_REQUEST)
        else:
            data = serializer.data
            user = request.user
            t = UserProfile(user=user, city=data['city'],  phone=data['phone'])
            t.save()
            request.DATA['id'] = t.pk # return id
            return Response(request.DATA, status=status.HTTP_201_CREATED)

    def put(self, request, todo_id):
        """ Update a todo """
        serializer = TodoSerializer(data=request.DATA)
        if not serializer.is_valid():
            return Response(serializer.errors, status=
                status.HTTP_400_BAD_REQUEST)
        else:
            data = serializer.data
            desc = data['description']
            done = data['done']
            t = Todo(id=todo_id, owner=request.user, description=desc,\
                     done=done, updated=datetime.now())
            t.save()
            return Response(status=status.HTTP_200_OK)

class GameEmailView2(APIView):
    permission_classes = ()

    def get(self, request, game_id):
        """ Get all todos """
        players = GameUsers.objects.filter(game_id=game_id)
        serializer = GameUsersSerializer2(players, many=True)
        return Response(serializer.data)

class MyGameUsersView(APIView):
    parser_classes = (JSONParser, )
    permission_classes = ()

    def get(self, request):
        """ Get all todos """
    #    mygames = GameUsers.objects.filter(user=request.user.id).values('game_id')
   #     players = GameUsers.objects.filter(game_id__in=mygames).values('game_id').annotate(total=Count('user'))
        players = GameUsers.objects.filter(user=request.user.id)
        #import pdb; pdb.set_trace()
        serializer = MyGamesSerializer(players, many=True)
        return Response(serializer.data)
        #return Response(players, status=status.HTTP_201_CREATED)

class GameUsersView(APIView):
    parser_classes = (JSONParser, )
    permission_classes = ()

    def get(self, request, game_id):
        """ Get all todos """
        players = GameUsers.objects.filter(game_id=game_id)
        serializer = GameUsersSerializer2(players, many=True)
        return Response(serializer.data)

    def post(self, request, game_id):
        """ Adding a new todo. """
        serializer = GameUsersSerializer(data=request.DATA)
        if not serializer.is_valid():
            return Response(serializer.errors, status=
                status.HTTP_400_BAD_REQUEST)
        else:
            data = serializer.data
            user = request.user
            userd = UserSerializer(user)
            email_choice = userd.data['profile']['email_choice']
            game_id = Game.objects.get(id=data['game_id'])
            gstatus = data['gstatus']
            t = GameUsers(user=user, game_id=game_id, gstatus=gstatus, email_choice=email_choice)
            t.save()
            request.DATA['id'] = t.pk # return id
            return Response(request.DATA, status=status.HTTP_201_CREATED)

    def put(self, request, game_id):
        """ Adding a new todo. """
        serializer = GameUsersSerializer(data=request.DATA)
        if not serializer.is_valid():
            return Response(serializer.errors, status=
                status.HTTP_400_BAD_REQUEST)
        else:
            data = serializer.data
            user = request.user
            game_id = Game.objects.get(id=data['game_id'])
            gstatus = data['gstatus']
            gstatus_id = data['gstatus_id']
            t = GameUsers(id=gstatus_id, user=user, game_id=game_id, gstatus=gstatus)
            t.save()
            request.DATA['id'] = t.pk # return id
            return Response(request.DATA, status=status.HTTP_201_CREATED)


class GameStatusView(APIView):
    parser_classes = (JSONParser, )
    permission_classes = ()

    def get(self, request, gstatus_id):
        players = GameUsers.objects.filter(id=gstatus_id)
        serializer = GameUsersSerializer2(players, many=True)
        return Response(serializer.data)

    def post(self, request, game_id):
        serializer = GameUsersSerializer(data=request.DATA)
        if not serializer.is_valid():
            return Response(serializer.errors, status=
                status.HTTP_400_BAD_REQUEST)
        else:
            data = serializer.data
            user = request.user
            game_id = Game.objects.get(id=data['game_id'])
            gstatus = data['gstatus']
            t = GameUsers(user=user, game_id=game_id, gstatus=gstatus)
            t.save()
            request.DATA['id'] = t.pk # return id
            return Response(request.DATA, status=status.HTTP_201_CREATED)

    def put(self, request, gstatus_id):
        serializer = GameUsersPutSerializer(data=request.DATA)
        if not serializer.is_valid():
            return Response(serializer.errors, status=
                status.HTTP_400_BAD_REQUEST)
        else:
            data = serializer.data
            user = request.user
            game_id = Game.objects.get(id=data['game_id'])
            gstatus = data['gstatus']
            email_choice = data['email_choice']
            t = GameUsers(id=gstatus_id, user=user, gstatus=gstatus, game_id=game_id,email_choice=email_choice)
            t.save()
            request.DATA['id'] = t.pk # return id
            #send_group_mail(game_id.id)
            return Response(request.DATA, status=status.HTTP_201_CREATED)


class UserGameStatusView(APIView):
#    permission_classes = (IsAuthenticated,)
    parser_classes = (JSONParser, )
    permission_classes = ()

    def get(self, request, game_id):
        """ Get all todos """
        players = GameUsers.objects.filter(game_id=game_id,user=request.user.id)
        #players = GameWeek.objects.all()
        #todos = Player.objects.filter(game=game_id)
        #players = GameWeek.objects.filter(owner=request.user.id)
        serializer = GameUsersSerializer2(players, many=True)
        return Response(serializer.data)

    def post(self, request, game_id):
        #import pdb; pdb.set_trace()
        """ Adding a new todo. """
        serializer = GameUsersSerializer(data=request.DATA)
        if not serializer.is_valid():
#            import pdb; pdb.set_trace()
            return Response(serializer.errors, status=
                status.HTTP_400_BAD_REQUEST)
        else:
            data = serializer.data
            user = request.user
            game_id = Game.objects.get(id=data['game_id'])
            #game_id = data['game_id'] 
            #week = data['week']
            gstatus = data['gstatus']
            t = GameUsers(user=user, game_id=game_id, gstatus=gstatus)
            t.save()
            request.DATA['id'] = t.pk # return id
            return Response(request.DATA, status=status.HTTP_201_CREATED)

    def put(self, request, gstatus_id):
        #import pdb; pdb.set_trace()
        """ Adding a new todo. """
 #       serializer = GameUsersSerializer(data=request.DATA)
        import pdb; pdb.set_trace()
        serializer = GameUsersPutSerializer(data=request.DATA)
#        import pdb; pdb.set_trace()
        if not serializer.is_valid():
#            import pdb; pdb.set_trace()
            return Response(serializer.errors, status=
                status.HTTP_400_BAD_REQUEST)
        else:
            data = serializer.data
            user = request.user
#            gstatus1 = Game.objects.get(id=game_status)
            #game_id = data['game_id'] 
            game_id = Game.objects.get(id=data['game_id'])
            #week = data['week']
            gstatus = data['gstatus']
            #gstatus_id = data['gstatus_id']
            t = GameUsers(id=gstatus_id, user=user, gstatus=gstatus, game_id=game_id)
            t.save()
            request.DATA['id'] = t.pk # return id
            return Response(request.DATA, status=status.HTTP_201_CREATED)


class GameEmailView(APIView):
    parser_classes = (JSONParser, )
    permission_classes = ()

    def get(self, request, gstatus_id):
        players = GameUsers.objects.filter(id=gstatus_id)
        serializer = GameUsersSerializer2(players, many=True)
        return Response(serializer.data)

    def post(self, request, game_id):
        serializer = GameUsersSerializer(data=request.DATA)
        if not serializer.is_valid():
            return Response(serializer.errors, status=
                status.HTTP_400_BAD_REQUEST)
        else:
            data = serializer.data
            user = request.user
            game_id = Game.objects.get(id=data['game_id'])
            gstatus = data['gstatus']
            t = GameUsers(user=user, game_id=game_id, gstatus=gstatus)
            t.save()
            request.DATA['id'] = t.pk # return id
            return Response(request.DATA, status=status.HTTP_201_CREATED)

    def put(self, request, gstatus_id):
        serializer = GameEmailPutSerializer(data=request.DATA)
        if not serializer.is_valid():
            return Response(serializer.errors, status=
                status.HTTP_400_BAD_REQUEST)
        else:
            data = serializer.data
      #      import pdb; pdb.set_trace()
            user = request.user
            game_id = Game.objects.get(id=data['game_id'])
            email_choice = data['email_choice']
            gstatus = data['gstatus']
            t = GameUsers(id=gstatus_id, user=user, email_choice=email_choice, game_id=game_id,gstatus=gstatus )
            t.save()
            request.DATA['id'] = t.pk # return id
            return Response(request.DATA, status=status.HTTP_201_CREATED)

class ContentView(APIView):
    parser_classes = (JSONParser, )
    permission_classes = ()

    def get(self, request, game_id):
        """ Get all todos """
        content = Content.objects.filter(game_id=game_id)
        serializer = ContentSerializer(content, many=True)
        return Response(serializer.data)

    def post(self, request, game_id):
        """ Adding a new todo. """
        serializer = ContentSerializer(data=request.DATA)
        if not serializer.is_valid():
#            import pdb; pdb.set_trace()
            return Response(serializer.errors, status=
                status.HTTP_400_BAD_REQUEST)
        else:
            data = serializer.data
            user = request.user
            #userd = UserSerializer(user)
            #email_choice = userd.data['profile']['email_choice']
            #game_id = data['game_id']
            game_id = Game.objects.get(id=data['game_id'])
            verbiage = data['verbiage']
            t = Content(user=user, game_id=game_id, verbiage=verbiage)
            t.save()
            request.DATA['id'] = t.pk # return id
            return Response(request.DATA, status=status.HTTP_201_CREATED)

    def put(self, request, game_id):
        """ Adding a new todo. """
        serializer = GameUsersSerializer(data=request.DATA)
        if not serializer.is_valid():
            return Response(serializer.errors, status=
                status.HTTP_400_BAD_REQUEST)
        else:
            data = serializer.data
            user = request.user
            game_id = Game.objects.get(id=data['game_id'])
            gstatus = data['gstatus']
            gstatus_id = data['gstatus_id']
            t = GameUsers(id=gstatus_id, user=user, game_id=game_id, gstatus=gstatus)
            t.save()
            request.DATA['id'] = t.pk # return id
            return Response(request.DATA, status=status.HTTP_201_CREATED)


class PhotoList(APIView):
    permission_classes = ()
    #permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    def get(self, request, format=None):
        photo = MyPhoto.objects.all()
        serializer = PhotoSerializer(photo, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        #serializer = PhotoSerializer(data=request.DATA, files=request.FILES)
        serializer = PhotoSerializer(data=request.data)

        if not serializer.is_valid():
           # import pdb; pdb.set_trace()
            return Response(serializer.errors, status=
                status.HTTP_400_BAD_REQUEST)
        else:
            data = serializer.data
            user = request.user
            #game_id = Game.objects.get(id=data['game_id'])
            image = data['image']
        #    url = data['url']
            t = Content(user=user, image=image)
            t.save()
            request.DATA['id'] = t.pk # return id
            return Response(request.DATA, status=status.HTTP_201_CREATED)



       #serializer = PhotoSerializer(data=request.DATA, files=request.FILES)
#       if serializer.is_valid():
#           serializer.save()
#           return Response(serializer.DATA, status=status.HTTP_201_CREATED)
#       return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#    def pre_save(self, obj):
#        obj.owner = self.request.user


class PhotoDetail(APIView):

    permission_classes = ()
    #permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    def get_object(self, pk):
        try:
            return MyPhoto.objects.get(pk=pk)
        except MyPhoto.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        photo = self.get_object(pk)
        serializer = PhotoSerializer(photo)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        photo = self.get_object(pk)
        serializer = PhotoSerializer(photo, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        photo = self.get_object(pk)
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def pre_save(self, obj):
        obj.owner = self.request.user


class FileUploadView(APIView):
    permission_classes = ()
    parser_classes = (FileUploadParser, )


    def post(self, request, format=None):
            up_file = request.FILES['file']
            with open("/tmp/" + up_file.name, "wb") as f:
                 f.write(up_file.read())
            reopen = open("/tmp/" + up_file.name, "rb")
            django_file = File(reopen)
            revsys = MyPhoto()
            revsys.name = "Revolution Systems"
            user = User.objects.get(pk=1)
            revsys.image =  up_file.name
            revsys.verbiage = request.data['verbiage'] 
            revsys.owner =  request.user
            revsys.image.save(up_file.name, django_file, save=True)

            return Response(request.DATA, status=status.HTTP_201_CREATED)


class uploadProfilePic(APIView):
    permission_classes = ()
    parser_classes = (FileUploadParser, )


    def post(self, request, format=None):
            up_file = request.FILES['file']
            with open("/tmp/" + up_file.name, "wb") as f:
                 f.write(up_file.read())
            reopen = open("/tmp/" + up_file.name, "rb")
            django_file = File(reopen)
            #revsys.name = "Revolution Systems"
            #user = User.objects.get(pk=1)
            #user = request.user
            revsys = Profile.objects.get(user_id=request.user.id)
            revsys.profile_pic =  up_file.name
#            import pdb; pdb.set_trace()
            #revsys.verbiage = request.data['verbiage'] 
            #revsys.owner =  request.user
            #revsys.profile_pic.save(up_file.name, django_file, save=True)
            revsys.profile_pic.save(up_file.name, django_file, save=True)
#            revsys.save()

            return Response(request.DATA, status=status.HTTP_201_CREATED)


