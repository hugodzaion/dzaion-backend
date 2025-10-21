# -*- coding: utf-8 -*-
"""
Módulo de Modelos para o App 'products'.

Este módulo define o catálogo central de todas as ofertas comerciais
do ecossistema, incluindo Tipos de Produto, Produtos (Módulos),
Ciclos de Faturamento e os Planos de Produto comercializáveis.

Author: Dzaion
Version: 0.4.0
"""
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import Permission
from core.models import BaseModel

def product_image_directory_path(instance, filename):
    """Gera o caminho para o upload da imagem do produto."""
    return f'products/{instance.product.id}/images/{filename}'

class ProductType(BaseModel):
    """
    Categoriza os tipos de produtos que o Dzaion vende.
    Ex: "Módulo de Assinatura", "Crédito de IA por Uso".
    """
    name = models.CharField(
        max_length=100,
        verbose_name='Nome Legível'
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código Interno',
        help_text='Ex: SUBSCRIPTION_MODULE, IA_USAGE_CREDIT'
    )

    class Meta:
        verbose_name = 'Tipo de Produto'
        verbose_name_plural = 'Tipos de Produtos'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(BaseModel):
    """
    Representa o "Lego" em si. O conceito do serviço oferecido.
    Ex: "Gestão de Clientes", "Módulo Escola de Tênis".
    """
    class ProductStatus(models.TextChoices):
        DRAFT = 'DRAFT', 'Rascunho'
        ACTIVE = 'ACTIVE', 'Ativo'
        ARCHIVED = 'ARCHIVED', 'Arquivado'

    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.PROTECT,
        verbose_name='Categoria do Produto'
    )
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Nome do Módulo'
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name='Identificador de URL'
    )
    description = models.TextField(
        verbose_name='Descrição da Funcionalidade'
    )
    icon = models.CharField(
        max_length=100,
        null=True, blank=True,
        verbose_name='Ícone',
        help_text='O nome de um ícone para ser usado no frontend (ex: fas fa-users).'
    )
    status = models.CharField(
        max_length=10,
        choices=ProductStatus.choices,
        default=ProductStatus.DRAFT,
        verbose_name='Status do Ciclo de Vida'
    )
    suggested_modules = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        verbose_name='Módulos Sugeridos',
        help_text='Outros módulos que podem ser oferecidos a quem assina este.'
    )
    granted_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        verbose_name='Permissões Concedidas',
        help_text='As "chaves" que este módulo adiciona aos papéis de administrador do assinante.'
    )

    class Meta:
        verbose_name = 'Produto (Módulo)'
        verbose_name_plural = 'Produtos (Módulos)'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Gera o slug automaticamente se ele não existir."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductImage(BaseModel):
    """
    Representa uma imagem de galeria para um Produto (Módulo),
    com campos para controle de exibição.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Produto (Módulo)'
    )
    image = models.ImageField(
        upload_to=product_image_directory_path,
        verbose_name='Arquivo de Imagem'
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Texto Alternativo',
        help_text='Descrição da imagem para acessibilidade.'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Ordem de Exibição',
        help_text='Menor número aparece primeiro.'
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name='É a Imagem Principal?',
        help_text='Marque para destacar esta como a imagem principal do produto.'
    )
    code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Código de Uso',
        help_text='Um código para uso do frontend (ex: "slider", "banner_full").'
    )

    class Meta:
        verbose_name = 'Imagem do Produto'
        verbose_name_plural = 'Imagens do Produto'
        ordering = ['order']


class BillingCycle(BaseModel):
    """
    Define um período de faturamento e uma oferta comercial associada.
    """
    class PeriodType(models.TextChoices):
        MONTHLY = 'MONTHLY', 'Mensal'
        QUARTERLY = 'QUARTERLY', 'Trimestral'
        SEMI_ANNUALLY = 'SEMI_ANNUALLY', 'Semestral'
        ANNUALLY = 'ANNUALLY', 'Anual'

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nome da Oferta',
        help_text='Ex: "Cobrança Mensal", "Anual com 20% de Desconto".'
    )
    period = models.CharField(
        max_length=15,
        choices=PeriodType.choices,
        verbose_name='Frequência de Cobrança'
    )
    discount_percentage = models.PositiveIntegerField(
        default=0,
        verbose_name='Percentual de Desconto',
        help_text='O incentivo que este ciclo oferece sobre o preço base.'
    )

    class Meta:
        verbose_name = 'Ciclo de Faturamento'
        verbose_name_plural = 'Ciclos de Faturamento'
        ordering = ['discount_percentage']

    def __str__(self):
        return self.name


class ProductPlan(BaseModel):
    """
    A oferta concreta que um cliente pode assinar, combinando um Produto,
    um preço e os termos de pagamento.
    """
    class PlanStatus(models.TextChoices):
        DRAFT = 'DRAFT', 'Rascunho'
        ACTIVE = 'ACTIVE', 'Ativo'
        ARCHIVED = 'ARCHIVED', 'Arquivado'

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='plans',
        verbose_name='Produto (Módulo)'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Nome do Plano',
        help_text='Ex: "Plano Básico", "Plano Profissional".'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Preço Base',
        help_text='O preço antes de qualquer desconto do ciclo de faturamento.'
    )
    billing_cycle = models.ForeignKey(
        BillingCycle,
        on_delete=models.PROTECT,
        verbose_name='Ciclo de Faturamento'
    )
    features = models.JSONField(
        default=list,
        verbose_name='Lista de Funcionalidades',
        help_text='A lista de itens incluídos neste plano.'
    )
    status = models.CharField(
        max_length=10,
        choices=PlanStatus.choices,
        default=PlanStatus.DRAFT,
        verbose_name='Disponibilidade'
    )

    class Meta:
        verbose_name = 'Plano de Produto'
        verbose_name_plural = 'Planos de Produtos'
        ordering = ['product', 'price']
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'name', 'billing_cycle'],
                name='unique_product_plan_offer'
            )
        ]

    def __str__(self):
        return f"{self.product.name} - {self.name} ({self.billing_cycle.name})"

