from directory.models import Organization, Department, Position
from django.db import models
from django.utils.translation import gettext_lazy as _

from restapp.models import BaseModel

GENDERS = (
    ('male', _('Male')),
    ('female', _('Female')),
)

class Employee(BaseModel):
    full_name = models.CharField(max_length=255, help_text=_("Hodim fio"))
    date_of_birthday = models.DateField(_('date of birthday'), null=True, blank=True, help_text=_("Tug‘ilgan sanasi"))
    gender = models.CharField(choices=GENDERS, max_length=6, null=True, blank=True, )
    phone_number = models.CharField(_("Phone number"), max_length=100, help_text=_("Telefon raqami"))
    organization = models.ForeignKey(Organization, related_name='employees', on_delete=models.SET_NULL, null=True,
                                     blank=True, help_text=_("Tashkilot"))
    department = models.ForeignKey(Department, related_name='employees', on_delete=models.SET_NULL, null=True,
                                   blank=True, help_text=_("Bo‘lim"))
    date_of_appointment = models.DateField(_('Date of appointment'), null=True, blank=True, help_text=_("Tug‘ilgan sanasi"))
    position = models.ForeignKey(Position, related_name='employees', on_delete=models.SET_NULL, null=True,
                                 blank=True, help_text=_("Lavozim"))
    region = models.ForeignKey("directory.Region", related_name='employees', on_delete=models.SET_NULL, null=True,
                               blank=True, help_text=_("Viloyat"))
    district = models.ForeignKey("directory.District", related_name='employees', on_delete=models.SET_NULL,
                                 null=True, blank=True, help_text=_("Tuman"))
    mahalla = models.ForeignKey("directory.Mahalla", related_name='employees', on_delete=models.SET_NULL,
                                 null=True, blank=True, help_text=_("Mahalla"))
    address = models.TextField(_("Address"), null=True, blank=True, help_text=_("Yashash manzili"))
    avatar = models.ImageField(upload_to='employee/%Y/%m/%d', null=True, blank=True, help_text=_("Profil rasmi"))
    sorting = models.IntegerField(_("Sorting"), null=True, blank=True, help_text=_("Sorting"))

    class Meta:
        verbose_name = _('Employee')
        verbose_name_plural = _('Employees')

    def __str__(self):
        return self.full_name if self.full_name else str(self.id)


class MahallaInformationCategory(BaseModel):
    name = models.CharField(max_length=255, null=True, blank=True, help_text=_("Nomi"))
    icon = models.TextField(null=True, blank=True, help_text=_("SVG icon"))

    class Meta:
        verbose_name = _('Mahalla Information Category')
        verbose_name_plural = _('Mahalla Information Categories')

    def __str__(self):
        return self.name if self.name else str(self.id)


class MahallaInformation(BaseModel):
    count = models.IntegerField(default=0, null=True, blank=True, help_text=_("Soni"))
    category = models.ForeignKey(MahallaInformationCategory, related_name='mahalla_informations', on_delete=models.SET_NULL,
                               null=True,
                               blank=True, help_text=_("Viloyat"))
    region = models.ForeignKey("directory.Region", related_name='mahalla_informations', on_delete=models.SET_NULL, null=True,
                               blank=True, help_text=_("Viloyat"))
    district = models.ForeignKey("directory.District", related_name='mahalla_informations', on_delete=models.SET_NULL,
                                 null=True, blank=True, help_text=_("Tuman"))
    mahalla = models.ForeignKey("directory.Mahalla", related_name='mahalla_informations', on_delete=models.SET_NULL,
                                null=True, blank=True, help_text=_("Mahalla"))

    class Meta:
        verbose_name = _('Mahalla Information')
        verbose_name_plural = _('Mahalla Informations')

    def __str__(self):
        return str(self.count) if self.count is not None else str(self.id)


class ObjectCategory(BaseModel):
    key = models.CharField(max_length=255, null=True, blank=True, help_text=_("Nomi"))
    name = models.CharField(max_length=255, null=True, blank=True, help_text=_("Nomi"))
    color = models.CharField(max_length=255, null=True, blank=True, help_text=_("Rang"))
    icon = models.TextField(null=True, blank=True, help_text=_("SVG icon"))
    icon_color = models.CharField(max_length=255, null=True, blank=True, help_text=_("Icon Rang"))

    class Meta:
        verbose_name = _('Object Category')
        verbose_name_plural = _('Object Categories')

    def __str__(self):
        return self.name if self.name else str(self.id)


class Object(BaseModel):
    name = models.CharField(max_length=100, null=True, blank=True, help_text=_("Nomi"))
    category = models.ForeignKey(ObjectCategory, related_name='category_objects', on_delete=models.SET_NULL, null=True,
                                     blank=True, help_text=_("Kategoriya"))
    organization = models.ForeignKey("directory.Organization", related_name='organization_objects', on_delete=models.SET_NULL,
                                     null=True, blank=True, help_text=_("Tashkilot"))
    full_name = models.CharField(max_length=255, help_text=_("Rahbar fio"))
    avatar = models.ImageField(upload_to='object_employee/%Y/%m/%d', null=True, blank=True, help_text=_("Profil rasmi"))
    phone_number = models.CharField(_("Phone number"), max_length=100, help_text=_("Telefon raqami"))
    address = models.TextField(_("Address"), null=True, blank=True, help_text=_("Yashash manzili"))
    coordinate_x = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata X"))
    coordinate_y = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata y"))

    class Meta:
        verbose_name = _('Object')
        verbose_name_plural = _('Objects')

    def __str__(self):
        return self.name if self.name else str(self.id)


# Jinoyat kategoriyasi
class CrimeCategory(BaseModel):
    name = models.CharField(max_length=255, null=True, blank=True, help_text=_("Nomi"))

    class Meta:
        verbose_name = _('Crime Category')
        verbose_name_plural = _('Crime Categories')

    def __str__(self):
        return self.name if self.name else self.id


# Mahallada sodir etilgan jonoyatchilik
class MahallaCrime(BaseModel):
    category = models.ForeignKey(CrimeCategory, related_name='crimes', on_delete=models.SET_NULL, null=True,
                                 blank=True, help_text=_("Jinoyat kategoriyasi"))
    date = models.DateField(_('Date'), null=True, blank=True, help_text=_("Jinoyat sodir etilgan sana"))
    article = models.CharField(max_length=255, help_text=_("Modda"))
    description = models.TextField(_("Description"), null=True, blank=True, help_text=_("Tasnif"))
    coordinate_x = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata X"))
    coordinate_y = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata y"))
    region = models.ForeignKey("directory.Region", related_name='mahalla_crimes', on_delete=models.SET_NULL,
                               null=True,
                               blank=True, help_text=_("Viloyat"))
    district = models.ForeignKey("directory.District", related_name='mahalla_crimes', on_delete=models.SET_NULL,
                                 null=True, blank=True, help_text=_("Tuman"))
    mahalla = models.ForeignKey("directory.Mahalla", related_name='mahalla_crimes', on_delete=models.SET_NULL,
                                null=True, blank=True, help_text=_("Mahalla"))

    class Meta:
        verbose_name = _('Mahalla Crime')
        verbose_name_plural = _('Mahalla Crimes')

    def __str__(self):
        return self.article if self.article else str(self.id)


# Patrolga biriktirilgan Avtomobillar
class PatrolCar(BaseModel):
    mobjectId = models.IntegerField(null=True, blank=True, help_text=_("Mobile ID"))
    mobject_name = models.CharField(max_length=255, null=True, blank=True, help_text=_("Nomi"))
    plate_number = models.CharField(max_length=255, null=True, blank=True, help_text=_("plate number"))
    imei = models.CharField(max_length=255, null=True, blank=True, help_text=_("imei"))
    brand_name = models.CharField(max_length=255, null=True, blank=True, help_text=_("brand Name"))
    group_name = models.CharField(max_length=255, null=True, blank=True, help_text=_("group Name"))
    last_date = models.DateField(null=True, blank=True, help_text=_("Last date"))
    coordinate_x = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata X"))
    coordinate_y = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata y"))


    class Meta:
        verbose_name = _('Patrol Car')
        verbose_name_plural = _('Patrol Cars')
        indexes = [
            models.Index(fields=["mobjectId"]),
        ]

    def __str__(self):
        return self.plate_number if self.plate_number else self.mobjectId


# Kamera malumtlari
class CameraInformation(BaseModel):
    class STATUS(models.TextChoices):
        INSTALLED = 'Installed', _('Installed')
        PLANNED = 'Planned', _('Planned')
    object_name = models.CharField(max_length=255, null=True, blank=True, help_text=_("Obyekt Nomi"))
    direction = models.CharField(max_length=255, null=True, blank=True, help_text=_("Yo'nalish"))
    status = models.CharField(max_length=30, choices=STATUS.choices,
                            verbose_name=_('Camera status'), help_text=_("Kamera holati"))
    ip_address = models.CharField(max_length=255, null=True, blank=True, help_text=_("Ip address"))
    region = models.ForeignKey("directory.Region", related_name='cameras', on_delete=models.SET_NULL, null=True,
                               blank=True, help_text=_("Viloyat"))
    district = models.ForeignKey("directory.District", related_name='cameras', on_delete=models.SET_NULL,
                                 null=True, blank=True, help_text=_("Tuman"))
    mahalla = models.ForeignKey("directory.Mahalla", related_name='cameras', on_delete=models.SET_NULL,
                                null=True, blank=True, help_text=_("Mahalla"))
    address = models.TextField(_("Address"), null=True, blank=True, help_text=_("Yashash manzili"))
    coordinate_x = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata X"))
    coordinate_y = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata y"))
    login = models.CharField(max_length=100, null=True, blank=True, help_text=_("Login"))
    parol = models.CharField(max_length=100, null=True, blank=True, help_text=_("parol"))
    camera_type = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kamer turi"))

    class Meta:
        verbose_name = _('Camera Information')
        verbose_name_plural = _('Camera Informations')

    def __str__(self):
        return self.ip_address if self.ip_address else self.object_name


# Ofis Kamera malumtlari
class OfficeCamera(BaseModel):
    object_name = models.CharField(max_length=255, null=True, blank=True, help_text=_("Obyekt Nomi"))
    direction = models.CharField(max_length=255, null=True, blank=True, help_text=_("Yo'nalish"))
    ip_address = models.CharField(max_length=255, null=True, blank=True, help_text=_("Ip address"))
    region = models.ForeignKey("directory.Region", related_name='office_cameras', on_delete=models.SET_NULL, null=True,
                               blank=True, help_text=_("Viloyat"))
    district = models.ForeignKey("directory.District", related_name='office_cameras', on_delete=models.SET_NULL,
                                 null=True, blank=True, help_text=_("Tuman"))
    mahalla = models.ForeignKey("directory.Mahalla", related_name='office_cameras', on_delete=models.SET_NULL,
                                null=True, blank=True, help_text=_("Mahalla"))
    address = models.TextField(_("Address"), null=True, blank=True, help_text=_("Yashash manzili"))
    coordinate_x = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata X"))
    coordinate_y = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata y"))
    login = models.CharField(max_length=100, null=True, blank=True, help_text=_("Login"))
    parol = models.CharField(max_length=100, null=True, blank=True, help_text=_("parol"))
    camera_type = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kamer turi"))
    camera_url = models.CharField(max_length=255, null=True, blank=True, help_text=_("Kamer turi"))

    class Meta:
        verbose_name = _('Office Camera')
        verbose_name_plural = _('Office Camera')

    def __str__(self):
        return self.ip_address if self.ip_address else self.object_name


class BazarCamera(BaseModel):
    class TYPE(models.TextChoices):
        DRB = "drb", _("DRB")
        FACE = "face", _("FACE")

    object_name = models.CharField(max_length=255, null=True, blank=True, help_text=_("Obyekt Nomi"))
    type = models.CharField(max_length=50, choices=TYPE.choices, null=True, blank=True, help_text=_("Kamera tip"))
    ip_address = models.CharField(max_length=255, null=True, blank=True, help_text=_("Ip address"))
    coordinate_x = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata X"))
    coordinate_y = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata y"))
    url = models.CharField(max_length=255, null=True, blank=True, help_text=_("Kamera url"))
    icon = models.TextField(null=True, blank=True, help_text=_("Kamera icon"))
    login = models.CharField(max_length=100, null=True, blank=True, help_text=_("Login"))
    parol = models.CharField(max_length=100, null=True, blank=True, help_text=_("parol"))
    region = models.ForeignKey("directory.Region", related_name='bazar_cameras', on_delete=models.SET_NULL, null=True,
                               blank=True, help_text=_("Viloyat"))
    district = models.ForeignKey("directory.District", related_name='bazar_cameras', on_delete=models.SET_NULL,
                                 null=True, blank=True, help_text=_("Tuman"))
    mahalla = models.ForeignKey("directory.Mahalla", related_name='bazar_cameras', on_delete=models.SET_NULL,
                                null=True, blank=True, help_text=_("Mahalla"))

    class Meta:
        verbose_name = _("Bazar Camera")
        verbose_name_plural = _("Bazar Cameras")

    def __str__(self):
        return f"{self.object_name}" or f"Bazar Camera #{self.pk}"


class Shop(BaseModel):
    """
    Do'kon: "Blok A - 1-do'kon"
    """
    class BlockType(models.TextChoices):
        A = "A", _("Blok A")
        B = "B", _("Blok B")

    block_type = models.CharField(max_length=1, choices=BlockType.choices, null=True, blank=True, help_text=_("Blok turi (A/B)"))
    shop_number = models.PositiveIntegerField(null=True, blank=True, help_text=_("Do'kon raqami"))
    code = models.CharField(max_length=120, null=True, blank=True, help_text=_("Kod (masalan: 'Blok A 1-do'kon')"))
    # Do'kon egasi
    owner_fio = models.CharField(max_length=255, null=True, blank=True, help_text=_("Do'kon egasi F.I.Sh"))
    owner_jshshir = models.CharField(max_length=20, null=True, blank=True, help_text=_("Do'kon egasi JSHSHIR"))
    owner_phone = models.CharField(max_length=30, null=True, blank=True, help_text=_("Do'kon egasi telefon raqami"))

    total_area = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text=_("Do'kon umumiy maydoni (kv.m)"))
    tenants_count = models.PositiveIntegerField(null=True, blank=True, help_text=_("Ijaraga olgan tadbirkor soni"))
    rented_area = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text=_("Ijaraga berilgan maydon (kv.m)"))

    class Meta:
        verbose_name = _("Shop")
        verbose_name_plural = _("Shops")
        indexes = [models.Index(fields=["block_type", "shop_number"]), models.Index(fields=["code"])]
        constraints = [
            models.UniqueConstraint(fields=["block_type", "shop_number"], name="uq_shop_block_type_shop_number"),
        ]

    def __str__(self):
        if self.code:
            return self.code
        if self.block_type and self.shop_number:
            return f"Blok {self.block_type} - {self.shop_number}-do'kon"
        return f"Shop #{self.pk}"


class ShopCamera(BaseModel):
    """
    Do'konda kameralari.
    """
    shop = models.ForeignKey(Shop, related_name="shop_cameras", on_delete=models.CASCADE, help_text=_("Do'kon"))
    url = models.CharField(max_length=255, null=True, blank=True, help_text=_("Kamera url"))

    class Meta:
        verbose_name = _("Shop Camera")
        verbose_name_plural = _("Shop Cameras")

    def __str__(self):
        return f"Shop Camera #{self.pk}"


class ShopTenant(BaseModel):
    """
    Do'konda faoliyat olib borayotgan tadbirkorlik subyekti (MCHJ, YTT ...)
    Bitta do'konda bir nechta tenant bo'lishi mumkin.
    """
    shop = models.ForeignKey(Shop, related_name="tenants", on_delete=models.CASCADE, help_text=_("Do'kon"))
    name = models.CharField(max_length=255, null=True, blank=True, help_text=_("Tadbirkorlik subyekti nomi"))
    # Rahbar ma'lumotlari
    leader_fio = models.CharField(max_length=255, null=True, blank=True, help_text=_("Rahbar F.I.SH"))
    leader_jshshir = models.CharField(max_length=20, null=True, blank=True, help_text=_("Rahbar JSHSHIR"))
    leader_phone = models.CharField(max_length=30, null=True, blank=True, help_text=_("Rahbar telefon raqami"))
    # Rekvizitlar
    stir = models.CharField(max_length=30, null=True, blank=True, help_text=_("STIR (INN)"))
    certificate_number = models.CharField(max_length=80, null=True, blank=True, help_text=_("Guvohnoma raqami"))
    employees_count = models.PositiveIntegerField(null=True, blank=True, help_text=_("Subyektda ishlaydigan xodimlar soni"))

    class Meta:
        verbose_name = _("Shop Tenant")
        verbose_name_plural = _("Shop Tenants")
        indexes = [models.Index(fields=["shop", "stir"]), models.Index(fields=["certificate_number"])]

    def __str__(self):
        return self.name or f"Tenant #{self.pk}"


class TenantEmployee(BaseModel):
    """
    Tenant (subyekt) xodimlari ro'yxati
    """
    tenant = models.ForeignKey(ShopTenant, related_name="employees", on_delete=models.CASCADE, help_text=_("Tadbirkorlik subyekti"))
    fio = models.CharField(max_length=255, null=True, blank=True, help_text=_("Xodim F.I.SH"))
    jshshir = models.CharField(max_length=20, null=True, blank=True, help_text=_("Xodim JSHSHIR"))
    phone = models.CharField(max_length=30, null=True, blank=True, help_text=_("Xodim telefon raqami"))

    class Meta:
        verbose_name = _("Tenant Employee")
        verbose_name_plural = _("Tenant Employees")

    def __str__(self):
        return self.fio or f"Employee #{self.pk}"


class ShopTradeStats(BaseModel):
    """
    Do'kon bo'yicha savdo / kassa / tashrif / xavfsizlik holati.
    Bu modelni "snapshot" sifatida yuritish mumkin (masalan kunlik/oylik yangilab borish).
    """
    class TaxType(models.TextChoices):
        VAT = "vat", _("QQS")
        MONTHLY_INCOME = "monthly_income", _("Oylik daromad solig'i")
        OTHER = "other", _("Boshqa")

    class ActivityStatus(models.TextChoices):
        ACTIVE = "active", _("FAOL")
        INACTIVE = "inactive", _("NOFAOL")

    class FireSafetyLevel(models.TextChoices):
        LOW = "low", _("Past")
        MEDIUM = "medium", _("O'rtacha")
        HIGH = "high", _("Yuqori")

    shop = models.OneToOneField(Shop, related_name="stats", on_delete=models.CASCADE, help_text=_("Do'kon"))
    # Soliq / kassa
    tax_type = models.CharField(max_length=50, choices=TaxType.choices, null=True, blank=True, help_text=_("Soliq turi"))
    cash_register_number = models.CharField(max_length=80, null=True, blank=True, help_text=_("Kassa apparat raqami"))
    # Yil boshidan savdo tushumi (3 kanal)
    ytd_okkm = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text=_("Yil boshidan tushum (OKKM)"))
    ytd_e_invoice = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text=_("Yil boshidan tushum (EHF)"))
    ytd_qr = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text=_("Yil boshidan tushum (QR)"))
    # Oy boshidan savdo tushumi
    mtd_okkm = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text=_("Oy boshidan tushum (OKKM)"))
    mtd_e_invoice = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text=_("Oy boshidan tushum (EHF)"))
    mtd_qr = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text=_("Oy boshidan tushum (QR)"))
    # Kun boshidan savdo tushumi
    dtd_okkm = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text=_("Kun boshidan tushum (OKKM)"))
    dtd_e_invoice = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text=_("Kun boshidan tushum (EHF)"))
    dtd_qr = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text=_("Kun boshidan tushum (QR)"))
    # Cheklar
    monthly_checks_count = models.PositiveIntegerField(null=True, blank=True, help_text=_("Berilgan oylik cheklar soni"))
    daily_checks_count = models.PositiveIntegerField(null=True, blank=True, help_text=_("Berilgan kunlik cheklar soni"))
    # Tashrif (video kuzatuv orqali)
    monthly_visitors = models.PositiveIntegerField(null=True, blank=True, help_text=_("1 oy davomida kirayotgan fuqarolar soni"))
    daily_visitors = models.PositiveIntegerField(null=True, blank=True, help_text=_("1 kun davomida kirayotgan fuqarolar soni"))
    # Holat / yong'in xavfsizligi
    activity_status = models.CharField(max_length=20, choices=ActivityStatus.choices, null=True, blank=True, help_text=_("Tadbirkorlik subyekti holati (FAOL/NOFAOL)"))
    fire_safety_level = models.CharField(max_length=20, choices=FireSafetyLevel.choices, null=True, blank=True, help_text=_("Yong'in xavfsizlik darajasi"))
    has_fire_alarm = models.BooleanField(default=False, help_text=_("Yong'indan xabar beruvchi qurilma bor-yo'qligi"))
    extinguisher_info = models.CharField(max_length=255, null=True, blank=True, help_text=_("Birlamchi yong'in o'chirish vositasi (Ognetushitel) turi/soni"))
    # Qizil toifa
    is_red_category = models.BooleanField(default=False, help_text=_("Qizil toifaga kirgan do'kon"))
    red_reason = models.CharField(max_length=255, null=True, blank=True, help_text=_("Qizilga kirgan sababi"))

    class Meta:
        verbose_name = _("Shop Trade Stats")
        verbose_name_plural = _("Shop Trade Stats")

    def __str__(self):
        return f"Stats: {self.shop}"
