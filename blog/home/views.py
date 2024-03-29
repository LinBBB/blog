from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from home.models import ArticleCategory,Article
from django.http.response import HttpResponseNotFound
# Create your views here.
class IndexView(View):
    def get(self,request):

        """
        1.获取所有分类信息
        2.接收用户点击的分类id
        3.根据分类id进行分类的查询
        4.获取分页参数
        5.根据分类信息查询文章数据
        6.创建分页器
        7.进行分页处理
        8.组织数据传递给模板
        """
        # 1.获取所有分类信息
        categories = ArticleCategory.objects.all()
        # 2.接收用户点击的分类id
        cat_id = request.GET.get('cat_id',1)
        # 3.根据分类id进行分类的查询
        try:
            category = ArticleCategory.objects.get(id=cat_id)
        except ArticleCategory.DoesNotExist:
            return HttpResponseNotFound('没有此分类')
        # 4.获取分页参数
        page_num = request.GET.get('page_num',1)
        page_size = request.GET.get('page_size',10)
        # 5.根据分类信息查询文章数据
        articles = Article.objects.filter(category=category)
        # 6.创建分页器
        from django.core.paginator import Paginator,EmptyPage
        paginator = Paginator(articles,per_page=page_size)
        # 7.进行分页处理
        try:
            page_articles = paginator.page(page_num)
        except EmptyPage:
            return HttpResponseNotFound('empty page')
        # 总页数
        total_page = paginator.num_pages

        # 8.组织数据传递给模板
        context = {
            'categories':categories,
            "category":category,
            "articles":page_articles,
            "page_size":page_size,
            "total_page":total_page,
            "page_num":page_num
        }

        return render(request,"index.html",context)

from home.models import Comment
class DetailView(View):
    def get(self,request):
        """
        1.接收文章id信息
        2.根据文章id进行文章数据查询
        3.查询分类数据
        获取分页请求参数
        根据文章信息查询评论数据
        创建分页器
        进行分页处理

        4.组织模板数据

        """
        # 1.接收文章id信息
        id = request.GET.get('id')
        # 2.根据文章id进行文章数据查询
        try:
            article = Article.objects.get(id=id)
        except Article.DoesNotExist:
            return render(request,"404.html")
        else:
            # 让浏览量+1
            article.total_views += 1
            article.save()
        # 3.查询分类数据
        categories = ArticleCategory.objects.all()

        # 查询浏览量前10的文章数据
        hot_articles = Article.objects.order_by("-total_views")[:9]


        # 获取分页请求参数
        page_size = request.GET.get("page_size",10)
        page_num = request.GET.get('page_num',1)
        # 根据文章信息查询评论数据
        comments = Comment.objects.filter(article=article).order_by('-created')
        # 获取评论总数
        total_count = comments.count()
        # 创建分页器
        from django.core.paginator import Paginator,EmptyPage
        paginator = Paginator(comments,page_size)
        # 进行分页处理
        try:
            page_comment = paginator.page(page_num)
        except EmptyPage:
            return HttpResponseNotFound("empty page")

        # 总页数
        total_page = paginator.num_pages

        # 4.组织模板数据
        context = {
            'categories':categories,
            'category':article.category,
            "article":article,
            "hot_articles":hot_articles,
            "total_count":total_count,
            "comments":page_comment,
            "page_size":page_size,
            "total_page":total_page,
            "page_num":page_num,
        }

        return render(request,"detail.html",context)

    def post(self,request):
        """
        1.先接收用户信息
        2.判断用户是否登录
        3.登录用户则可以接收form数据
            3.1接收评论数据
            验证文章是否存在
            3.2保存评论数据
            3.3修改文章的评论数量
        4.未3登录用户则跳转到登陆页面
        """
        # 1.先接收用户信息
        user = request.user
        # 2.判断用户是否登录
        if user and user.is_authenticated:
            # 3.登录用户则可以接收form数据
            #     3.1接收评论数据
            id = request.POST.get('id')
            content = request.POST.get('content')
            #     验证文章是否存在

            try:
                article = Article.objects.get(id=id)
            except Article.DoesNotExist:
                return HttpResponseNotFound("没有此文章")
            #     3.2保存评论数据
            Comment.objects.create(
                content=content,
                article = article,
                user=user,
            )
            #     3.3修改文章的评论数量
            article.comments_count += 1
            article.save()
            # 刷新
            path = reverse('home:detail')+'?id={}'.format(article.id)
            return redirect(path)
        else:
            # 4.未3登录用户则跳转到登陆页面
            return redirect(reverse('users:login'))