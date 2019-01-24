from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.views.generic import ListView, CreateView, UpdateView

from .models import Question, Choice
from .forms import ChoiceForm, QuestionForm

# Create your views here.
# FBV: function based view
# CBV: class based view


def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')

    query = request.GET.get('q')
    # print(query)
    if query:
        latest_question_list = latest_question_list.filter(
            Q(question_text__icontains=query) |
            Q(author__username__icontains=query)
        ).distinct()

    form = QuestionForm()
    context = {
        'latest_question_list': latest_question_list,
        'current_user': {'user': request.user, 'is_login': request.user.is_authenticated},
        'form': form
        }
    return render(request, 'bbs/index.html', context)


class QuestionListView(ListView):
    # 数据来源哪个表
    model = Question
    # 从数据库Question表获取所有数据列表的名字
    context_object_name = 'latest_question_list'
    # 渲染模板
    template_name = 'bbs/index.html'
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        # 获取模板上下文变量额外的变量
        context = super().get_context_data(**kwargs)
        context['current_user'] = {
            'user': self.request.user, 
            'is_login': self.request.user.is_authenticated
            }
        context['form'] = QuestionForm()
        print(context)
        return context

    def get_queryset(self):
        # 过滤所获得的数据
        queryset = super().get_queryset()
        print(queryset)
        query = self.request.GET.get('q')
        # print(query)
        if query:
            return queryset.filter(
                Q(question_text__icontains=query) |
                Q(author__username__icontains=query)
            ).distinct()
        return queryset.order_by('-pub_date')


@login_required
def my_page(request):
    latest_question_list = Question.objects.order_by('-pub_date').filter(author=request.user)

    form = QuestionForm()
    context = {
        'latest_question_list': latest_question_list,
        'current_user': {'user': request.user, 'is_login': request.user.is_authenticated},
        'form': form
        }
    return render(request, 'bbs/my_page.html', context)


def detail(request, question_id):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]

    form = ChoiceForm()

    question = get_object_or_404(Question, pk=question_id)
    context = {
        'latest_question_list': latest_question_list,
        'question': question,
        'current_user': {'user': request.user, 'is_login': request.user.is_authenticated},
        'form': form
        }
    return render(request, 'bbs/detail.html', context)

@login_required
def topic(request):
    # 取到数据
    if request.method == 'POST':
        # 判断pk存在的情况下，只更新数据
        pk = request.POST.get('pk')
        if pk:
            question = get_object_or_404(Question, pk=pk)
            print('get question by pk: ', pk, question)
            question.question_text = request.POST['question_text']
            question.save()
            return HttpResponseRedirect(reverse('bbs:detail', args=(pk,)))

        form = QuestionForm(request.POST, request.FILES or None)
        print('form:', form, request.FILES)
        # 判断合法，并保存
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()
    # 返回页面
    return HttpResponseRedirect(reverse('bbs:index'))


@method_decorator(login_required, name='dispatch')
class TopicUpdateView(UpdateView):
    # 要更新的表
    model = Question
    # 渲染模板
    template_name = 'bbs/detail.html'

    def post(self, request, *args, **kwargs):
        # 如果method为post
        # 判断pk存在的情况下，只更新数据
        pk = request.POST.get('pk')
        if pk:
            question = get_object_or_404(Question, pk=pk)
            question.question_text = request.POST['question_text']
            question.save()
            return HttpResponseRedirect(reverse('bbs:detail', args=(pk,)))


class TopicCreateView(CreateView):
    # 要存入的model
    model = Question
    # 渲染模板
    template_name = 'bbs/index.html'
    # 数据库相应的字段 
    fields = ('question_text', 'picture')

    def form_valid(self, form):
        # 字段合法后会执行这个函数，执行完成后会把字段存入数据库
        """If the form is valid, save the associated model."""
        question = form.save(commit=False)
        question.author = self.request.user
        question.save()
        # 进入表单提交成功的页面
        return redirect('bbs:index')



def reply_old(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        reply_name = request.POST['reply_name']
        reply_text = request.POST['reply_text']
        print(reply_name, reply_text)

        if reply_name and reply_text:
            question.choice_set.create(
                choice_text = reply_text,
                author = reply_name
            )
            question.save()
        else:
            return render(request, 'bbs/detail.html', {
            'question': question,
            'error_message': "没有数据！",
        })
    except (KeyError):
        # Redisplay the question voting form.
        return render(request, 'bbs/detail.html', {
            'question': question,
            'error_message': "传值出错！！",
        })
    else:
        return HttpResponseRedirect(reverse('bbs:detail', args=(question.id,)))

def reply(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        if request.method == 'POST':
            form = ChoiceForm(request.POST, request.FILES or None)
            print('form:', form, request.FILES)
            if form.is_valid():
                reply = form.save(commit=False)
                print('reply: ', reply, type(reply))
                reply.author = request.user
                reply.question = question
                # reply.picture = request.FILES['picture']
                reply.save()

    except (KeyError):
        # Redisplay the question voting form.
        return render(request, 'bbs/detail.html', {
            'question': question,
            'error_message': "传值出错！！",
        })
    else:
        return HttpResponseRedirect(reverse('bbs:detail', args=(question.id,)))