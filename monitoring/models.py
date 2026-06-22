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
    gom = models.ForeignKey("directory.Gom", related_name='employees', on_delete=models.SET_NULL,
                                 null=True, blank=True, help_text=_("Gom"))
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
    gom = models.ForeignKey("directory.Gom", related_name='gom_informations', on_delete=models.SET_NULL,
                                 null=True, blank=True, help_text=_("Gom"))
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
    region = models.ForeignKey("directory.Region", related_name='mahalla_objects', on_delete=models.SET_NULL, null=True,
                               blank=True, help_text=_("Viloyat"))
    district = models.ForeignKey("directory.District", related_name='mahalla_objects', on_delete=models.SET_NULL,
                                 null=True, blank=True, help_text=_("Tuman"))
    gom = models.ForeignKey("directory.Gom", related_name='gom_objects', on_delete=models.SET_NULL,
                                 null=True, blank=True, help_text=_("Gom"))
    mahalla = models.ForeignKey("directory.Mahalla", related_name='mahalla_objects', on_delete=models.SET_NULL,
                                null=True, blank=True, help_text=_("Mahalla"))

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
    gom = models.ForeignKey("directory.Gom", related_name='gom_crimes', on_delete=models.SET_NULL,
                                 null=True, blank=True, help_text=_("Gom"))
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
    gom = models.ForeignKey("directory.Gom", related_name='cameras', on_delete=models.SET_NULL,
                                 null=True, blank=True, help_text=_("Gom"))
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
    gom = models.ForeignKey("directory.Gom", related_name='office_cameras', on_delete=models.SET_NULL,
                                 null=True, blank=True, help_text=_("Gom"))
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
    class CAMERA_TYPE(models.TextChoices):
        DRB = "drb", _("DRB")
        FACE = "face", _("FACE")

    class TYPE(models.TextChoices):
        INPUT = "input", _("Input")
        OUTPUT = "output", _("Output")

    class LOCATION_TYPE(models.TextChoices):
        MALIKA = "malika", _("Malika")
        CICILIZATION = "civilization", _("Civilization")

    object_name = models.CharField(max_length=255, null=True, blank=True, help_text=_("Obyekt Nomi"))
    type = models.CharField(max_length=50, choices=TYPE.choices, null=True, blank=True, help_text=_("Tip"))
    camera_type = models.CharField(max_length=50, choices=CAMERA_TYPE.choices, null=True, blank=True, help_text=_("Kamera tip"))
    location_type = models.CharField(max_length=100, choices=LOCATION_TYPE.choices, null=True, blank=True, help_text=_("Lokatsiya tip"))
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
    is_active = models.BooleanField(default=True, help_text=_("Is active"))

    class Meta:
        verbose_name = _("Bazar Camera")
        verbose_name_plural = _("Bazar Cameras")

    def __str__(self):
        return f"{self.object_name}" or f"Bazar Camera #{self.pk}"


class CarFlow(models.Model):
    class LOCATION_TYPE(models.TextChoices):
        MALIKA = "malika", _("Malika")
        CIVILIZATION = "civilization", _("Civilization")

    class TYPE(models.TextChoices):
        IN = "in", _("Kirdi")
        OUT = "out", _("Chiqdi")

    camera = models.ForeignKey(
        BazarCamera, related_name='car_flows',
        on_delete=models.SET_NULL, null=True, blank=True
    )
    ip_address = models.CharField(max_length=255, help_text=_("Kamera IP"))
    location_type = models.CharField(
        max_length=100, choices=LOCATION_TYPE.choices,
        null=True, blank=True, help_text=_("Lokatsiya")
    )
    region_soato = models.IntegerField(null=True, blank=True, help_text=_("Viloyat SOATO"))
    type = models.CharField(max_length=10, choices=TYPE.choices, help_text=_("Kirdi/Chiqdi"))
    recorded_at = models.DateTimeField(help_text=_("Qayd etilgan vaqt"))
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Car Flow")
        verbose_name_plural = _("Car Flows")
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.ip_address} | {self.type} | {self.recorded_at}"


class Shop(BaseModel):
    """
    Do'kon: "Blok A - 1-do'kon"
    """

    class BlockType(models.TextChoices):
        BLOK_A = "A", _("Blok A")
        BLOK_B = "B", _("Blok B")
        BLOK_G = "G", _("Blok G")
        BLOK_J = "J", _("Blok J")
        SAVDO_MARKAZ = "SM", _("Merkato")
        SKLAD = "SK", _("Sklad")
        OFIS = "OF", _("Ofis")
        PARKOVKA = "P", _("Avtoturargoh")

    block_type = models.CharField(max_length=100, choices=BlockType.choices, null=True, blank=True, help_text=_("Blok turi (A/B)"))
    shop_number = models.CharField(max_length=255, null=True, blank=True, help_text=_("Do'kon raqami"))
    code = models.CharField(max_length=100, null=True, blank=True, help_text=_("Do'kon kod"))
    cadastr_number = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kadastr raqami"))
    owner_company_name = models.CharField(max_length=255, null=True, blank=True, help_text=_("Do'kon egasiga tegishli MCHJ nomi"))
    owner_fio = models.CharField(max_length=255, null=True, blank=True, help_text=_("Do'kon egasi F.I.Sh"))
    owner_jshshir = models.CharField(max_length=255, null=True, blank=True, help_text=_("Do'kon egasi JSHSHIR"))
    owner_phone = models.CharField(max_length=255, null=True, blank=True, help_text=_("Do'kon egasi telefon raqami"))
    avatar = models.ImageField(upload_to='owner/%Y/%m/%d', null=True, blank=True, help_text=_("Do'kon egasi rasmi"))
    total_area = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text=_("Do'kon umumiy maydoni (kv.m)"))
    tenants_count = models.PositiveIntegerField(null=True, blank=True, help_text=_("Ijaraga olgan tadbirkor soni"))

    class Meta:
        verbose_name = _("Shop")
        verbose_name_plural = _("Shops")
        indexes = [
            models.Index(fields=["block_type", "shop_number"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["block_type", "shop_number"], name="uq_shop_block_type_shop_number"),
        ]

    def __str__(self):
        if self.block_type and self.shop_number:
            return f"Blok {self.block_type} - {self.shop_number}-do'kon"
        return f"Shop #{self.pk}"


class ShopCamera(BaseModel):
    """
    Do'konda kameralari.
    """
    shop = models.ForeignKey(Shop, related_name="shop_cameras", on_delete=models.CASCADE,
                             null=True, blank=True, help_text=_("Do'kon (perimetr kamerasi bo'sh bo'lishi mumkin)"))
    title = models.CharField(max_length=255, null=True, blank=True, help_text=_("Izoh"))
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
    class BusinessType(models.TextChoices):
        YTT = "ytt", _("YTT")
        LEGAL = "legal", _("Yuridik")
        OTHER = "other", _("Boshqa")

    class TaxType(models.TextChoices):
        VAT = "vat", _("QQS")
        MONTHLY_INCOME = "monthly_income", _("Aylanmadan olinadigan soliq")
        OTHER = "other", _("Boshqa")

    class ActivityStatus(models.TextChoices):
        ACTIVE = "active", _("FAOL")
        INACTIVE = "inactive", _("NOFAOL")

    class FireSafetyLevel(models.TextChoices):
        LOW = "low", _("Past")
        MEDIUM = "medium", _("O'rtacha")
        HIGH = "high", _("Yuqori")

    rented_area = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text=_("Ijaraga berilgan maydon (kv.m)"))
    rent_month_sum = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text=_("Ijara oylik summasi"))
    rent_total_sum = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text=_("Ijara shartnoma bo'yicha jami summasi"))
    business_type = models.CharField(max_length=255, choices=BusinessType.choices, null=True, blank=True)
    tax_type = models.CharField(max_length=100, choices=TaxType.choices, null=True, blank=True, help_text=_("Soliq turi"))
    activity_status = models.CharField(max_length=100, choices=ActivityStatus.choices, null=True, blank=True, help_text=_("Tadbirkorlik subyekti holati (FAOL/NOFAOL)"))
    shop = models.ForeignKey(Shop, related_name="tenants", on_delete=models.CASCADE, help_text=_("Do'kon"))
    name = models.CharField(max_length=255, null=True, blank=True, help_text=_("Faoliyat olib borayotgan Tadbirkorlik subyekti Rahbarining"))
    # Rahbar ma'lumotlari
    leader_fio = models.CharField(max_length=255, null=True, blank=True, help_text=_("Rahbar F.I.SH"))
    leader_jshshir = models.CharField(max_length=255, null=True, blank=True, help_text=_("Rahbar JSHSHIR"))
    leader_phone = models.CharField(max_length=255, null=True, blank=True, help_text=_("Rahbar telefon raqami"))
    avatar = models.ImageField(upload_to='lider/%Y/%m/%d', null=True, blank=True, help_text=_("Rahbar rasmi"))
    # Rekvizitlar
    stir = models.CharField(max_length=255, null=True, blank=True, help_text=_("STIR (INN)"))
    certificate_number = models.CharField(max_length=255, null=True, blank=True, help_text=_("Guvohnoma raqami"))
    employees_count = models.PositiveIntegerField(null=True, blank=True, help_text=_("Subyektda ishlaydigan xodimlar soni"))
    trade_type = models.CharField(max_length=255, null=True, blank=True, help_text=_("Savdo turi"))
    cash_register_number_vat = models.CharField(max_length=255, null=True, blank=True, help_text=_("Kassa apparat raqami (QQS)"))
    cash_register_number_turnover = models.CharField(max_length=255, null=True, blank=True, help_text=_("Kassa apparat raqami (Aylanma soliq)"))
    # Yil boshidan savdo tushumi
    ytd_okkm_vat = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text=_("Yil boshidan tushum OKKM (QQS)"))
    ytd_okkm_turnover = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text=_("Yil boshidan tushum OKKM (Aylanma soliq)"))
    ytd_e_payment_vat = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text=_("Yil boshidan tushum Elektron to'lov (QQS)"))
    ytd_e_payment_turnover = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text=_("Yil boshidan tushum Elektron to'lov (Aylanma soliq)"))
    # Oy boshidan savdo tushumi
    mtd_okkm_vat = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text=_("Oy boshidan tushum OKKM (QQS)"))
    mtd_okkm_turnover = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text=_("Oy boshidan tushum OKKM (Aylanma soliq)"))
    mtd_e_payment_vat = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text=_("Oy boshidan tushum Elektron to'lov (QQS)"))
    mtd_e_payment_turnover = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text=_("Oy boshidan tushum Elektron to'lov (Aylanma soliq)"))
    # Kun boshidan savdo tushumi
    dtd_okkm_vat = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text=_("Kun boshidan tushum OKKM (QQS)"))
    dtd_okkm_turnover = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text=_("Kun boshidan tushum OKKM (Aylanma soliq)"))
    dtd_e_payment_vat = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text=_("Kun boshidan tushum Elektron to'lov (QQS)"))
    dtd_e_payment_turnover = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text=_("Kun boshidan tushum Elektron to'lov (Aylanma soliq)"))
    # Cheklar
    monthly_checks_count_vat = models.PositiveIntegerField(null=True, blank=True, help_text=_("Berilgan oylik cheklar soni (QQS)"))
    monthly_checks_count_turnover = models.PositiveIntegerField(null=True, blank=True, help_text=_("Berilgan oylik cheklar soni (Aylanma soliq)"))
    daily_checks_count_vat = models.PositiveIntegerField(null=True, blank=True, help_text=_("Berilgan kunlik cheklar soni (QQS)"))
    daily_checks_count_turnover = models.PositiveIntegerField(null=True, blank=True, help_text=_("Berilgan kunlik cheklar soni (Aylanma soliq)"))
    # Tashrif (video kuzatuv orqali)
    monthly_visitors = models.PositiveIntegerField(null=True, blank=True, help_text=_("1 oy davomida kirayotgan fuqarolar soni"))
    daily_visitors = models.PositiveIntegerField(null=True, blank=True, help_text=_("1 kun davomida kirayotgan fuqarolar soni"))
    # Holat / yong'in xavfsizligi

    fire_safety_level = models.CharField(max_length=255, choices=FireSafetyLevel.choices, null=True, blank=True, help_text=_("Yong'in xavfsizlik darajasi"))
    has_fire_alarm = models.BooleanField(default=False, help_text=_("Yong'indan xabar beruvchi qurilma bor-yo'qligi"))
    extinguisher_info = models.CharField(max_length=255, null=True, blank=True, help_text=_("Birlamchi yong'in o'chirish vositasi (Ognetushitel) turi/soni"))
    # Qizil toifa
    is_red_category = models.BooleanField(default=False, help_text=_("Qizil toifaga kirgan do'kon"))
    red_reason = models.CharField(max_length=255, null=True, blank=True, help_text=_("Qizilga kirgan sababi"))

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
    jshshir = models.CharField(max_length=255, null=True, blank=True, help_text=_("Xodim JSHSHIR"))
    phone = models.CharField(max_length=255, null=True, blank=True, help_text=_("Xodim telefon raqami"))
    avatar = models.ImageField(upload_to='tenemployee/%Y/%m/%d', null=True, blank=True, help_text=_("Hodim rasmi"))

    class Meta:
        verbose_name = _("Tenant Employee")
        verbose_name_plural = _("Tenant Employees")

    def __str__(self):
        return self.fio or f"Employee #{self.pk}"


class CenterOfCivilization(BaseModel):
    class CAMERA_TYPE(models.TextChoices):
        DRB = "drb", _("DRB")
        FACE = "face", _("FACE")

    class TYPE(models.TextChoices):
        INPUT = "input", _("Input")
        OUTPUT = "output", _("Output")

    object_name = models.CharField(max_length=255, null=True, blank=True, help_text=_("Obyekt Nomi"))
    type = models.CharField(max_length=50, choices=TYPE.choices, null=True, blank=True, help_text=_("Tip"))
    camera_type = models.CharField(max_length=50, choices=CAMERA_TYPE.choices, null=True, blank=True, help_text=_("Kamera tip"))
    ip_address = models.CharField(max_length=255, null=True, blank=True, help_text=_("Ip address"))
    coordinate_x = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata X"))
    coordinate_y = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata y"))
    url = models.CharField(max_length=255, null=True, blank=True, help_text=_("Kamera url"))
    icon = models.TextField(null=True, blank=True, help_text=_("Kamera icon"))
    login = models.CharField(max_length=100, null=True, blank=True, help_text=_("Login"))
    parol = models.CharField(max_length=100, null=True, blank=True, help_text=_("parol"))
    region = models.ForeignKey("directory.Region", related_name='civilization_cameras', on_delete=models.SET_NULL, null=True,
                               blank=True, help_text=_("Viloyat"))
    district = models.ForeignKey("directory.District", related_name='civilization_cameras', on_delete=models.SET_NULL,
                                 null=True, blank=True, help_text=_("Tuman"))
    mahalla = models.ForeignKey("directory.Mahalla", related_name='civilization_cameras', on_delete=models.SET_NULL,
                                null=True, blank=True, help_text=_("Mahalla"))
    is_active = models.BooleanField(default=True, help_text=_("Is active"))

    class Meta:
        verbose_name = _("Center of civilization")
        verbose_name_plural = _("Center of civilizations")

    def __str__(self):
        return f"{self.object_name}" or f"Center of civilization #{self.pk}"


class ShopCrime(BaseModel):
    """
    Do'konga biriktirilgan jinoyat/huquqbuzarlik yozuvi (HTML matn).
    """
    shop = models.ForeignKey(
        Shop, related_name="crimes", on_delete=models.CASCADE,
        null=True, blank=True, help_text=_("Do'kon")
    )
    malika_bozor = models.CharField(
        max_length=255, null=True, blank=True, help_text=_("Malika bozor (bo'lim/joy)")
    )
    date = models.DateTimeField(null=True, blank=True, help_text=_("Jinoyat sodir etilgan sana va vaqt"))
    content = models.TextField(help_text=_("Jinoyat tavsifi (HTML)"))

    class Meta:
        verbose_name = _("Shop Crime")
        verbose_name_plural = _("Shop Crimes")
        ordering = ["-created_time"]

    def __str__(self):
        return f"Crime #{self.pk} — {self.shop}"


class MFYCitizen(BaseModel):
    class CATEGORY(models.TextChoices):
        RUHIY = "ruhiy", _("Ruhiy kasallar")
        JANJAL = "janjal", _("Janjalkash oilalar")
        NARKO = "narko", _("Narkomanlar")

    full_name = models.CharField(max_length=255, null=True, blank=True, help_text=_("F.I.SH"))
    address = models.CharField(max_length=500, null=True, blank=True, help_text=_("Yashash manzili"))
    phone = models.CharField(max_length=50, null=True, blank=True, help_text=_("Telefon raqami"))
    avatar = models.ImageField(upload_to='mfy/citizens/', null=True, blank=True, help_text=_("Fuqaro rasmi"))

    category = models.CharField(max_length=20, choices=CATEGORY.choices, null=True, blank=True, help_text=_("Toifa"))

    degree = models.CharField(max_length=100, null=True, blank=True, help_text=_("Darajasi (ruhiy uchun)"))
    type = models.CharField(max_length=100, null=True, blank=True, help_text=_("Turi (narko uchun)"))

    coordinate_x = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata X"))
    coordinate_y = models.CharField(max_length=100, null=True, blank=True, help_text=_("Kordinata y"))

    region = models.ForeignKey("directory.Region", related_name='mfy_citizens', on_delete=models.SET_NULL, null=True, blank=True, help_text=_("Viloyat"))
    district = models.ForeignKey("directory.District", related_name='mfy_citizens', on_delete=models.SET_NULL, null=True, blank=True, help_text=_("Tuman"))
    gom = models.ForeignKey("directory.Gom", related_name='mfy_citizens', on_delete=models.SET_NULL,
                            null=True, blank=True, help_text=_("Gom"))
    mahalla = models.ForeignKey("directory.Mahalla", related_name='mfy_citizens', on_delete=models.SET_NULL, null=True, blank=True, help_text=_("Mahalla"))

    is_active = models.BooleanField(default=True, help_text=_("Is active"))

    class Meta:
        verbose_name = _("MFY Citizen")
        verbose_name_plural = _("MFY Citizens")

    def __str__(self):
        return f"{self.full_name}" or f"Citizen #{self.pk}"


class FacturaRevenueDaily(models.Model):
    """
    Soliq faktura integratsiyasidan yig'ilgan kunlik savdo/soliq tarixi.
    Dashboard grafigi (xafta/oy/yil) shu jadvaldan o'qiydi.

    Davriy (cron) sync har bir sellerTin bo'yicha faktura'larni olib,
    kun bo'yicha yig'adi va shu yerga yozadi (upsert).
    """
    date = models.DateField(help_text=_("Faktura sanasi (facturaDate)"), db_index=True)
    seller_tin = models.CharField(max_length=20, help_text=_("Sotuvchi STIR"))
    sales = models.DecimalField(max_digits=20, decimal_places=2, default=0,
                                help_text=_("Kunlik savdo (deliverySumWithVat yig'indisi)"))
    tax = models.DecimalField(max_digits=20, decimal_places=2, default=0,
                              help_text=_("Kunlik QQS (vatSum yig'indisi)"))
    factura_count = models.PositiveIntegerField(default=0, help_text=_("Faktura soni"))
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Factura Revenue Daily")
        verbose_name_plural = _("Factura Revenue Daily")
        unique_together = ("date", "seller_tin")

    def __str__(self):
        return f"{self.date} | {self.seller_tin} | {self.sales}"


class OkkmRevenueDaily(models.Model):
    """
    OKKM (onlayn-kassa / NKM cheklar) kunlik tushum tarixi (tin bo'yicha).
    Dashboard grafigi factura (FacturaRevenueDaily) bilan birga shu yerdan o'qiydi.

    Soliqda OKKM ni kunlarga bo'lib beradigan arzon endpoint yo'q, shuning uchun
    har KUN uchun get_cheque_statistics(tin, kun, kun) alohida chaqirilib upsert
    qilinadi: kunlik sync bugunni, backfill command o'tgan kunlarni to'ldiradi.
    """
    date = models.DateField(db_index=True, help_text=_("Chek sanasi"))
    tin = models.CharField(max_length=20, help_text=_("STIR"))
    turnover = models.DecimalField(max_digits=20, decimal_places=2, default=0,
                                   help_text=_("Kunlik OKKM savdo (turnover)"))
    vat = models.DecimalField(max_digits=20, decimal_places=2, default=0,
                              help_text=_("Kunlik OKKM QQS (vat)"))
    cheque_count = models.PositiveIntegerField(default=0, help_text=_("Cheklar soni"))
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("OKKM Revenue Daily")
        verbose_name_plural = _("OKKM Revenue Daily")
        unique_together = ("date", "tin")

    def __str__(self):
        return f"{self.date} | {self.tin} | {self.turnover}"


class TaxRevenue(models.Model):
    """
    Soliq tushumi (company-account, payTax) — har tin x har soliq kodi uchun
    JORIY snapshot: kunlik (bugun) / oylik (oy boshidan) / yillik (yil boshidan).

    Celery sync (sync_tax_revenue_task) har faol ijarachi tin i uchun belgilangan
    soliq kodlari (1,32,36,38,46,100,186) bo'yicha 3 davrni so'rab upsert qiladi.
    Dashboard endpoint kodlar bo'yicha barcha tin lar yig'indisini qaytaradi.
    """
    tin = models.CharField(max_length=20, db_index=True, help_text=_("STIR"))
    tax_code = models.PositiveIntegerField(help_text=_("Soliq kodi (taxCode)"))
    dtd_pay = models.DecimalField(max_digits=20, decimal_places=2, default=0,
                                  help_text=_("Bugun to'langan soliq (payTax)"))
    mtd_pay = models.DecimalField(max_digits=20, decimal_places=2, default=0,
                                  help_text=_("Oy boshidan to'langan soliq (payTax)"))
    ytd_pay = models.DecimalField(max_digits=20, decimal_places=2, default=0,
                                  help_text=_("Yil boshidan to'langan soliq (payTax)"))
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Tax Revenue")
        verbose_name_plural = _("Tax Revenue")
        unique_together = ("tin", "tax_code")

    def __str__(self):
        return f"{self.tin} | {self.tax_code} | {self.ytd_pay}"


class TaxRevenueMonthly(models.Model):
    """
    Soliq tushumi (company-account payTax) — OYLIK TARIX: har (tin, tax_code, year,
    month) uchun SHU OYDA to'langan soliq (period = oy boshidan oy oxirigacha).

    TaxRevenue (snapshot) dan farqi — tarixiy oylar saqlanadi. sync_tax_revenue_monthly
    to'ldiradi: o'tgan oylar o'zgarmaydi, joriy oy yangilanib boradi. Dashboard
    (oylik/yillik) va reports/tax-revenue (oy filteri) SHU jadvaldan o'qiydi.
    """
    tin = models.CharField(max_length=20, db_index=True, help_text=_("STIR"))
    tax_code = models.PositiveIntegerField(help_text=_("Soliq kodi (taxCode)"))
    year = models.PositiveIntegerField(help_text=_("Yil"))
    month = models.PositiveIntegerField(help_text=_("Oy (1..12)"))
    pay_tax = models.DecimalField(max_digits=20, decimal_places=2, default=0,
                                  help_text=_("Shu oyda to'langan soliq (payTax)"))
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Tax Revenue Monthly")
        verbose_name_plural = _("Tax Revenue Monthly")
        unique_together = ("tin", "tax_code", "year", "month")
        indexes = [models.Index(fields=["year", "month", "tax_code"])]

    def __str__(self):
        return f"{self.tin} | {self.tax_code} | {self.year}-{self.month:02d} | {self.pay_tax}"


class DamafonCall(models.Model):
    """
    Damafon (intercom) qo'ng'iroqlari TARIXI — mikroservis `incoming_call` hodisasi.

    Damafon listener (management command) mikroservis WS ni tinglaydi va har bir
    incoming_call ni shu yerga yozadi (tarix). Frontendning JONLI oqimi esa
    DamafonEventConsumer (/ws/damafon/) orqali mikroservis /ws iga shaffof ko'prik
    bilan boradi — bu jadval faqat qo'ng'iroq tarixini saqlaydi.
    Qurilmalar mikroservis DB sida (biz proxy qilamiz). location_id = damafon
    `location_id` (= directory.Mahalla.id).
    """
    remote_damafon_id = models.PositiveIntegerField(null=True, blank=True,
                                                    help_text=_("Mikroservis damafon id"))
    damafon_name = models.CharField(max_length=255, blank=True, default="")
    host = models.CharField(max_length=100, blank=True, default="")
    call_id = models.CharField(max_length=255, blank=True, default="")
    stream = models.CharField(max_length=100, blank=True, default="")
    location_id = models.PositiveIntegerField(null=True, blank=True, db_index=True,
                                              help_text=_("Mahalla id (damafon location_id)"))
    received_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _("Damafon Call")
        verbose_name_plural = _("Damafon Calls")
        ordering = ("-received_at",)

    def __str__(self):
        return f"{self.received_at} | {self.damafon_name} | {self.call_id}"