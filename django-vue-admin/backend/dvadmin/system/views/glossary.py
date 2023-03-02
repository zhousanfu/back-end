#!python3.8
# coding=utf-8
'''
 Author: Sanfor Chow
 Date: 2022-11-24 14:49:42
 LastEditors: Sanfor Chow
 LastEditTime: 2022-11-25 09:05:09
 FilePath: /zhihui_api_backend/django-vue-admin/backend/dvadmin/system/views/glossary.py
'''
from rest_framework import serializers

from dvadmin.system.models import GlossaryLibrary, GlossaryTerms, GlossaryNode
from dvadmin.utils.json_response import DetailResponse, SuccessResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet

# Node
class GlossaryNodeSerializer(CustomModelSerializer):
    """
    节点-序列化器
    """
    node = serializers.SerializerMethodField()
    parent_name = serializers.CharField(read_only=True, source='parent.node')

    def get_node(self, obj):
        return obj.node
    
    def get_has_children(self, obj: GlossaryNode):
        return GlossaryNode.objects.filter(parent_id=obj.id).count()

    def get_review_label(self, instance):
        review = instance.review
        if review == 1:
            return "审核通过"
        return "未审核"
    
    class Meta:
        model = GlossaryNode
        fields = "__all__"

class GlossaryNodeViewSet(CustomModelViewSet):
    """
    节点任务接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = GlossaryNode.objects.all()
    serializer_class = GlossaryNodeSerializer
    filter_fields = ['node']
    # permission_classes = []


# Library
class GlossaryLibrarySerializer(CustomModelSerializer):
    """
    术语任务-序列化器
    """
    library_name = serializers.SerializerMethodField()

    def get_library_name(self, obj):
        return obj.library_name

    def get_has_children(self, obj: GlossaryLibrary):
        return GlossaryLibrary.objects.filter(parent_id=obj.id).count()

    def get_review_label(self, instance):
        review = instance.review
        if review == 1:
            return "审核通过"
        return "未审核"
    
    class Meta:
        model = GlossaryLibrary
        fields = "__all__"
        read_only_fields = ["id"]

class GlossaryLibraryViewSet(CustomModelViewSet):
    """
    术语任务接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = GlossaryLibrary.objects.all()
    serializer_class = GlossaryLibrarySerializer
    filter_fields = ['library_name', ]
    # permission_classes = []


# TermsImport
class GlossaryTermsSerializer(CustomModelSerializer):
    """
    术语管理-序列化器
    """
    library_name = serializers.ReadOnlyField(source='library.library')
    node_name = serializers.ReadOnlyField(source='node.node')
    parent_name = serializers.CharField(read_only=True, source='parent.term_name')
    has_children = serializers.SerializerMethodField()
    review_label = serializers.SerializerMethodField()

    def get_has_children(self, obj: GlossaryTerms):
        return GlossaryTerms.objects.filter(parent_id=obj.id).count()

    def get_review_label(self, instance):
        review = instance.review
        if review == 1:
            return "审核通过"
        return "未审核"

    class Meta:
        model = GlossaryTerms
        fields = '__all__'
        read_only_fields = ["id"]

class GlossaryTermsInitSerializer(CustomModelSerializer):
    """
    递归深度获取数信息(用于生成初始化json文件)
    """
    children = serializers.SerializerMethodField()

    def get_children(self, obj: GlossaryTerms):
        data = []
        instance = GlossaryTerms.objects.filter(parent_id=obj.id)
        if instance:
            serializer = GlossaryTermsInitSerializer(instance=instance, many=True)
            data = serializer.data
        return data

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        children = self.initial_data.get('children')
        if children:
            for menu_data in children:
                menu_data['parent'] = instance.id
                filter_data = {
                    "term_name": menu_data['term_name'],
                    "parent": menu_data['parent']
                }
                instance_obj = GlossaryTerms.objects.filter(**filter_data).first()
                if instance_obj and not self.initial_data.get('reset'):
                    continue
                serializer = GlossaryTermsInitSerializer(instance_obj, data=menu_data, request=self.request)
                serializer.is_valid(raise_exception=True)
                serializer.save()

        return instance

    class Meta:
        model = GlossaryTerms
        fields = ['node', 'term_name', 'code', 'synonymous', 'review', 'parent', 'creator', 'dept_belong_id',
                  'children']
        extra_kwargs = {
            'creator': {'write_only': True},
            'dept_belong_id': {'write_only': True}
        }
        read_only_fields = ['id', 'children']

class GlossaryTermsCreateUpdateSerializer(CustomModelSerializer):
    """
    术语管理 创建/更新时的列化器
    """

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.term_belong_id = instance.id
        instance.save()
        return instance

    class Meta:
        model = GlossaryTerms
        fields = '__all__'

class ExportGlossaryTermsSerializer(CustomModelSerializer):
    """
    术语导出
    """
    creator_name = serializers.SlugRelatedField(slug_field="name", source="creator", read_only=True)
    library_name = serializers.SlugRelatedField(slug_field="library_name", source='library', read_only=True)
    node_name = serializers.SlugRelatedField(slug_field="node", source='node', read_only=True)
    parent_name = serializers.CharField(read_only=True, source='parent.term_name')
    dept_name = serializers.CharField(source="dept.name", default="")
    dept_owner = serializers.CharField(source="dept.owner", default="")

    class Meta:
        model = GlossaryTerms
        fields = ('library_name', 'node_name', 'term_name', 'synonymous', 'creator_name', 'create_datetime', 'parent_name', 'dept_name', 'dept_owner',)

class GlossaryTermsImportSerializer(CustomModelSerializer):
    """
    术语导入
    """    
    creator_name = serializers.SlugRelatedField(slug_field="name", source="creator", read_only=True)
    library_name = serializers.SlugRelatedField(slug_field="library_name", source='library', read_only=True)
    parent_name = serializers.CharField(read_only=True, source='parent.term_name')
    dept_name = serializers.CharField(source="dept.name", default="")
    dept_owner = serializers.CharField(source="dept.owner", default="")
    
    def save(self, **kwargs):
        data = super().save(**kwargs)
        data.save()
        return data

    class Meta:
        model = GlossaryTerms
        exclude = ('library', 'term_name', 'synonymous', 'parent')

class GlossaryTermsViewSet(CustomModelViewSet):
    """
    术语管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = GlossaryTerms.objects.all()
    serializer_class = GlossaryTermsSerializer
    create_serializer_class = GlossaryTermsCreateUpdateSerializer
    update_serializer_class = GlossaryTermsCreateUpdateSerializer
    filter_fields = ['library', 'term_name', 'synonymous', 'parent', 'node']
    search_fields = ['synonymous', 'term_name']
    # 导入
    import_serializer_class = GlossaryTermsImportSerializer
    import_field_dict = {'library_name':'术语库名称', 'term_name':'术语', 'synonymous':'同义词', 'parent_name':'上级术语'}
    # 导出
    export_field_label = ('术语库名称', '节点', '术语', '同义词', '创建者', '创建时间', '上级术语', '部门名称', '部门负责人',)
    export_serializer_class = ExportGlossaryTermsSerializer

    extra_filter_backends = []

    def list(self, request, *args, **kwargs):
        # 如果懒加载，则只返回父级
        queryset = self.filter_queryset(self.get_queryset())
        lazy = self.request.query_params.get('lazy')
        parent = self.request.query_params.get('parent')
        if lazy:
            # 如果懒加载模式，返回全部
            if not parent:
                if self.request.user.is_superuser:
                    queryset = queryset.filter(parent__isnull=True)
                else:
                    queryset = queryset.filter(id=self.request.user.glossaryterms_id)
            serializer = self.get_serializer(queryset, many=True, request=request)
            return SuccessResponse(data=serializer.data, msg="获取成功")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, request=request)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, request=request)
        return SuccessResponse(data=serializer.data, msg="获取成功")

    def term_lazy_tree(self, request, *args, **kwargs):
        parent = self.request.query_params.get('parent')
        queryset = self.filter_queryset(self.get_queryset())
        if not parent:
            if self.request.user.is_superuser:
                queryset = queryset.filter(parent__isnull=True)
            else:
                queryset = queryset.filter(id=self.request.user.glossaryterms_id)
        # data = queryset.filter(status=True).order_by('sort').values('term_name', 'id', 'parent')
        data = queryset.filter().order_by('term_name').values('term_name', 'id', 'parent')
        return DetailResponse(data=data, msg="获取成功")