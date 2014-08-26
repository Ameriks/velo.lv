# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines for those models you wish to give write DB access
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models

# These are legacy models from www.velo.lv. It is planned to migrate all data from www.velo.lv to mans.velo.lv,
# but it's still in progress. :)

class Ev68RAcepollsOptions(models.Model):
    id = models.IntegerField(primary_key=True)
    poll_id = models.IntegerField()
    text = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    color = models.CharField(max_length=6)
    ordering = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_acepolls_options'

class Ev68RAcepollsPolls(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    published = models.IntegerField()
    publish_up = models.DateTimeField()
    publish_down = models.DateTimeField(blank=True, null=True)
    params = models.TextField()
    access = models.IntegerField()
    lag = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_acepolls_polls'

class Ev68RAcepollsVotes(models.Model):
    id = models.BigIntegerField(primary_key=True)
    date = models.DateTimeField()
    option_id = models.IntegerField()
    poll_id = models.IntegerField()
    ip = models.IntegerField()
    user_id = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'ev68r_acepolls_votes'

class Ev68RAkProfiles(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=255)
    configuration = models.TextField(blank=True)
    filters = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'ev68r_ak_profiles'

class Ev68RAkStats(models.Model):
    id = models.BigIntegerField(primary_key=True)
    description = models.CharField(max_length=255)
    comment = models.TextField(blank=True)
    backupstart = models.DateTimeField()
    backupend = models.DateTimeField()
    status = models.CharField(max_length=8)
    origin = models.CharField(max_length=30)
    type = models.CharField(max_length=30)
    profile_id = models.BigIntegerField()
    archivename = models.TextField(blank=True)
    absolute_path = models.TextField(blank=True)
    multipart = models.IntegerField()
    tag = models.CharField(max_length=255, blank=True)
    filesexist = models.IntegerField()
    remote_filename = models.CharField(max_length=1000, blank=True)
    total_size = models.BigIntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_ak_stats'

class Ev68RAkStorage(models.Model):
    tag = models.CharField(primary_key=True, max_length=255)
    lastupdate = models.DateTimeField()
    data = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'ev68r_ak_storage'

class Ev68RAssets(models.Model):
    id = models.IntegerField(primary_key=True)
    parent_id = models.IntegerField()
    lft = models.IntegerField()
    rgt = models.IntegerField()
    level = models.IntegerField()
    name = models.CharField(unique=True, max_length=50)
    title = models.CharField(max_length=100)
    rules = models.CharField(max_length=5120)
    class Meta:
        managed = False
        db_table = 'ev68r_assets'

class Ev68RAssociations(models.Model):
    id = models.CharField(max_length=50)
    context = models.CharField(max_length=50)
    key = models.CharField(max_length=32)
    class Meta:
        managed = False
        db_table = 'ev68r_associations'

class Ev68RBannerClients(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    extrainfo = models.TextField()
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    metakey = models.TextField()
    own_prefix = models.IntegerField()
    metakey_prefix = models.CharField(max_length=255)
    purchase_type = models.IntegerField()
    track_clicks = models.IntegerField()
    track_impressions = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_banner_clients'

class Ev68RBannerTracks(models.Model):
    track_date = models.DateTimeField()
    track_type = models.IntegerField()
    banner_id = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_banner_tracks'

class Ev68RBanners(models.Model):
    id = models.IntegerField(primary_key=True)
    cid = models.IntegerField()
    type = models.IntegerField()
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    imptotal = models.IntegerField()
    impmade = models.IntegerField()
    clicks = models.IntegerField()
    clickurl = models.CharField(max_length=200)
    state = models.IntegerField()
    catid = models.IntegerField()
    description = models.TextField()
    custombannercode = models.CharField(max_length=2048)
    sticky = models.IntegerField()
    ordering = models.IntegerField()
    metakey = models.TextField()
    params = models.TextField()
    own_prefix = models.IntegerField()
    metakey_prefix = models.CharField(max_length=255)
    purchase_type = models.IntegerField()
    track_clicks = models.IntegerField()
    track_impressions = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    publish_up = models.DateTimeField()
    publish_down = models.DateTimeField()
    reset = models.DateTimeField()
    created = models.DateTimeField()
    language = models.CharField(max_length=7)
    class Meta:
        managed = False
        db_table = 'ev68r_banners'

class Ev68RCategories(models.Model):
    id = models.IntegerField(primary_key=True)
    asset_id = models.IntegerField()
    parent_id = models.IntegerField()
    lft = models.IntegerField()
    rgt = models.IntegerField()
    level = models.IntegerField()
    path = models.CharField(max_length=255)
    extension = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    note = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    published = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    access = models.IntegerField(blank=True, null=True)
    params = models.TextField()
    metadesc = models.CharField(max_length=1024)
    metakey = models.CharField(max_length=1024)
    metadata = models.CharField(max_length=2048)
    created_user_id = models.IntegerField()
    created_time = models.DateTimeField()
    modified_user_id = models.IntegerField()
    modified_time = models.DateTimeField()
    hits = models.IntegerField()
    language = models.CharField(max_length=7)
    class Meta:
        managed = False
        db_table = 'ev68r_categories'

class Ev68RContactDetails(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    con_position = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    suburb = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=100, blank=True)
    telephone = models.CharField(max_length=255, blank=True)
    fax = models.CharField(max_length=255, blank=True)
    misc = models.TextField(blank=True)
    image = models.CharField(max_length=255, blank=True)
    imagepos = models.CharField(max_length=20, blank=True)
    email_to = models.CharField(max_length=255, blank=True)
    default_con = models.IntegerField()
    published = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    ordering = models.IntegerField()
    params = models.TextField()
    user_id = models.IntegerField()
    catid = models.IntegerField()
    access = models.IntegerField(blank=True, null=True)
    mobile = models.CharField(max_length=255)
    webpage = models.CharField(max_length=255)
    sortname1 = models.CharField(max_length=255)
    sortname2 = models.CharField(max_length=255)
    sortname3 = models.CharField(max_length=255)
    language = models.CharField(max_length=7)
    created = models.DateTimeField()
    created_by = models.IntegerField()
    created_by_alias = models.CharField(max_length=255)
    modified = models.DateTimeField()
    modified_by = models.IntegerField()
    metakey = models.TextField()
    metadesc = models.TextField()
    metadata = models.TextField()
    featured = models.IntegerField()
    xreference = models.CharField(max_length=50)
    publish_up = models.DateTimeField()
    publish_down = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'ev68r_contact_details'

class Ev68RContent(models.Model):
    id = models.IntegerField(primary_key=True)
    asset_id = models.IntegerField()
    title = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    title_alias = models.CharField(max_length=255)
    introtext = models.TextField()
    fulltext = models.TextField()
    state = models.IntegerField()
    sectionid = models.IntegerField()
    mask = models.IntegerField()
    catid = models.IntegerField()
    created = models.DateTimeField()
    created_by = models.IntegerField()
    created_by_alias = models.CharField(max_length=255)
    modified = models.DateTimeField()
    modified_by = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    publish_up = models.DateTimeField()
    publish_down = models.DateTimeField()
    images = models.TextField()
    urls = models.TextField()
    attribs = models.CharField(max_length=5120)
    version = models.IntegerField()
    parentid = models.IntegerField()
    ordering = models.IntegerField()
    metakey = models.TextField()
    metadesc = models.TextField()
    access = models.IntegerField()
    hits = models.IntegerField()
    metadata = models.TextField()
    featured = models.IntegerField()
    language = models.CharField(max_length=7)
    xreference = models.CharField(max_length=50)
    class Meta:
        managed = False
        db_table = 'ev68r_content'

class Ev68RContentFrontpage(models.Model):
    content_id = models.IntegerField(primary_key=True)
    ordering = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_content_frontpage'

class Ev68RContentRating(models.Model):
    content_id = models.IntegerField(primary_key=True)
    rating_sum = models.IntegerField()
    rating_count = models.IntegerField()
    lastip = models.CharField(max_length=50)
    class Meta:
        managed = False
        db_table = 'ev68r_content_rating'

class Ev68RCoreLogSearches(models.Model):
    search_term = models.CharField(max_length=128)
    hits = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_core_log_searches'

class Ev68RDocman(models.Model):
    id = models.IntegerField(primary_key=True)
    catid = models.IntegerField()
    dmname = models.TextField()
    dmdescription = models.TextField(blank=True)
    dmdate_published = models.DateTimeField()
    dmowner = models.IntegerField()
    dmfilename = models.TextField()
    published = models.IntegerField()
    dmurl = models.TextField(blank=True)
    dmcounter = models.IntegerField(blank=True, null=True)
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    approved = models.IntegerField()
    dmthumbnail = models.TextField(blank=True)
    dmlastupdateon = models.DateTimeField(blank=True, null=True)
    dmlastupdateby = models.IntegerField()
    dmsubmitedby = models.IntegerField()
    dmmantainedby = models.IntegerField(blank=True, null=True)
    dmlicense_id = models.IntegerField(blank=True, null=True)
    dmlicense_display = models.IntegerField()
    access = models.IntegerField()
    attribs = models.TextField()
    class Meta:
        managed = False
        db_table = 'ev68r_docman'

class Ev68RDocmanCategories(models.Model):
    id = models.IntegerField(primary_key=True)
    parent_id = models.IntegerField()
    title = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    image = models.CharField(max_length=255)
    section = models.CharField(max_length=50)
    image_position = models.CharField(max_length=30)
    description = models.TextField()
    published = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    editor = models.CharField(max_length=50, blank=True)
    ordering = models.IntegerField()
    access = models.IntegerField()
    count = models.IntegerField()
    params = models.TextField()
    class Meta:
        managed = False
        db_table = 'ev68r_docman_categories'

class Ev68RDocmanGroups(models.Model):
    groups_id = models.IntegerField(primary_key=True)
    groups_name = models.TextField()
    groups_description = models.TextField(blank=True)
    groups_access = models.IntegerField()
    groups_members = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'ev68r_docman_groups'

class Ev68RDocmanHistory(models.Model):
    id = models.IntegerField(primary_key=True)
    doc_id = models.IntegerField()
    revision = models.IntegerField()
    his_date = models.DateTimeField()
    his_who = models.IntegerField()
    his_obs = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'ev68r_docman_history'

class Ev68RDocmanLicenses(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    license = models.TextField()
    class Meta:
        managed = False
        db_table = 'ev68r_docman_licenses'

class Ev68RDocmanLog(models.Model):
    id = models.IntegerField(primary_key=True)
    log_docid = models.IntegerField()
    log_ip = models.TextField()
    log_datetime = models.DateTimeField()
    log_user = models.IntegerField()
    log_browser = models.TextField(blank=True)
    log_os = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'ev68r_docman_log'

class Ev68RExtensions(models.Model):
    extension_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20)
    element = models.CharField(max_length=100)
    folder = models.CharField(max_length=100)
    client_id = models.IntegerField()
    enabled = models.IntegerField()
    access = models.IntegerField(blank=True, null=True)
    protected = models.IntegerField()
    manifest_cache = models.TextField()
    params = models.TextField()
    custom_data = models.TextField()
    system_data = models.TextField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    ordering = models.IntegerField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'ev68r_extensions'

class Ev68RFacebookJoomlaConnect(models.Model):
    joomla_userid = models.IntegerField(primary_key=True)
    facebook_userid = models.BigIntegerField()
    joined_date = models.IntegerField()
    linked = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_facebook_joomla_connect'

class Ev68RFaqbookItems(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    catid = models.IntegerField()
    published = models.IntegerField()
    content = models.TextField()
    creator = models.IntegerField()
    ordering = models.IntegerField()
    votes_up = models.IntegerField()
    votes_down = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    access = models.IntegerField()
    params = models.TextField(blank=True)
    email = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'ev68r_faqbook_items'

class Ev68RFinderFilters(models.Model):
    filter_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    state = models.IntegerField()
    created = models.DateTimeField()
    created_by = models.IntegerField()
    created_by_alias = models.CharField(max_length=255)
    modified = models.DateTimeField()
    modified_by = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    map_count = models.IntegerField()
    data = models.TextField()
    params = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'ev68r_finder_filters'

class Ev68RFinderLinks(models.Model):
    link_id = models.IntegerField(primary_key=True)
    url = models.CharField(max_length=255)
    route = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    indexdate = models.DateTimeField()
    md5sum = models.CharField(max_length=32, blank=True)
    published = models.IntegerField()
    state = models.IntegerField(blank=True, null=True)
    access = models.IntegerField(blank=True, null=True)
    language = models.CharField(max_length=8)
    publish_start_date = models.DateTimeField()
    publish_end_date = models.DateTimeField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    list_price = models.FloatField()
    sale_price = models.FloatField()
    type_id = models.IntegerField()
    object = models.TextField()
    class Meta:
        managed = False
        db_table = 'ev68r_finder_links'

class Ev68RFinderLinksTerms0(models.Model):
    link_id = models.IntegerField()
    term_id = models.IntegerField()
    weight = models.FloatField()
    class Meta:
        managed = False
        db_table = 'ev68r_finder_links_terms0'

class Ev68RFinderLinksTerms1(models.Model):
    link_id = models.IntegerField()
    term_id = models.IntegerField()
    weight = models.FloatField()
    class Meta:
        managed = False
        db_table = 'ev68r_finder_links_terms1'

class Ev68RFinderLinksTerms2(models.Model):
    link_id = models.IntegerField()
    term_id = models.IntegerField()
    weight = models.FloatField()
    class Meta:
        managed = False
        db_table = 'ev68r_finder_links_terms2'

class Ev68RFinderLinksTerms3(models.Model):
    link_id = models.IntegerField()
    term_id = models.IntegerField()
    weight = models.FloatField()
    class Meta:
        managed = False
        db_table = 'ev68r_finder_links_terms3'

class Ev68RFinderLinksTerms4(models.Model):
    link_id = models.IntegerField()
    term_id = models.IntegerField()
    weight = models.FloatField()
    class Meta:
        managed = False
        db_table = 'ev68r_finder_links_terms4'

class Ev68RFinderLinksTerms5(models.Model):
    link_id = models.IntegerField()
    term_id = models.IntegerField()
    weight = models.FloatField()
    class Meta:
        managed = False
        db_table = 'ev68r_finder_links_terms5'

class Ev68RFinderLinksTerms6(models.Model):
    link_id = models.IntegerField()
    term_id = models.IntegerField()
    weight = models.FloatField()
    class Meta:
        managed = False
        db_table = 'ev68r_finder_links_terms6'

class Ev68RFinderLinksTerms7(models.Model):
    link_id = models.IntegerField()
    term_id = models.IntegerField()
    weight = models.FloatField()
    class Meta:
        managed = False
        db_table = 'ev68r_finder_links_terms7'

class Ev68RFinderLinksTerms8(models.Model):
    link_id = models.IntegerField()
    term_id = models.IntegerField()
    weight = models.FloatField()
    class Meta:
        managed = False
        db_table = 'ev68r_finder_links_terms8'

class Ev68RFinderLinksTerms9(models.Model):
    link_id = models.IntegerField()
    term_id = models.IntegerField()
    weight = models.FloatField()
    class Meta:
        managed = False
        db_table = 'ev68r_finder_links_terms9'

class Ev68RFinderLinksTermsa(models.Model):
    link_id = models.IntegerField()
    term_id = models.IntegerField()
    weight = models.FloatField()
    class Meta:
        managed = False
        db_table = 'ev68r_finder_links_termsa'

class Ev68RFinderLinksTermsb(models.Model):
    link_id = models.IntegerField()
    term_id = models.IntegerField()
    weight = models.FloatField()
    class Meta:
        managed = False
        db_table = 'ev68r_finder_links_termsb'

class Ev68RFinderLinksTermsc(models.Model):
    link_id = models.IntegerField()
    term_id = models.IntegerField()
    weight = models.FloatField()
    class Meta:
        managed = False
        db_table = 'ev68r_finder_links_termsc'

class Ev68RFinderLinksTermsd(models.Model):
    link_id = models.IntegerField()
    term_id = models.IntegerField()
    weight = models.FloatField()
    class Meta:
        managed = False
        db_table = 'ev68r_finder_links_termsd'

class Ev68RFinderLinksTermse(models.Model):
    link_id = models.IntegerField()
    term_id = models.IntegerField()
    weight = models.FloatField()
    class Meta:
        managed = False
        db_table = 'ev68r_finder_links_termse'

class Ev68RFinderLinksTermsf(models.Model):
    link_id = models.IntegerField()
    term_id = models.IntegerField()
    weight = models.FloatField()
    class Meta:
        managed = False
        db_table = 'ev68r_finder_links_termsf'

class Ev68RFinderTaxonomy(models.Model):
    id = models.IntegerField(primary_key=True)
    parent_id = models.IntegerField()
    title = models.CharField(max_length=255)
    state = models.IntegerField()
    access = models.IntegerField()
    ordering = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_finder_taxonomy'

class Ev68RFinderTaxonomyMap(models.Model):
    link_id = models.IntegerField()
    node_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_finder_taxonomy_map'

class Ev68RFinderTerms(models.Model):
    term_id = models.IntegerField(primary_key=True)
    term = models.CharField(unique=True, max_length=75)
    stem = models.CharField(max_length=75)
    common = models.IntegerField()
    phrase = models.IntegerField()
    weight = models.FloatField()
    soundex = models.CharField(max_length=75)
    links = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_finder_terms'

class Ev68RFinderTermsCommon(models.Model):
    term = models.CharField(max_length=75)
    language = models.CharField(max_length=3)
    class Meta:
        managed = False
        db_table = 'ev68r_finder_terms_common'

class Ev68RFinderTokens(models.Model):
    term = models.CharField(max_length=75)
    stem = models.CharField(max_length=75)
    common = models.IntegerField()
    phrase = models.IntegerField()
    weight = models.FloatField()
    context = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_finder_tokens'

class Ev68RFinderTokensAggregate(models.Model):
    term_id = models.IntegerField()
    map_suffix = models.CharField(max_length=1)
    term = models.CharField(max_length=75)
    stem = models.CharField(max_length=75)
    common = models.IntegerField()
    phrase = models.IntegerField()
    term_weight = models.FloatField()
    context = models.IntegerField()
    context_weight = models.FloatField()
    total_weight = models.FloatField()
    class Meta:
        managed = False
        db_table = 'ev68r_finder_tokens_aggregate'

class Ev68RFinderTypes(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(unique=True, max_length=100)
    mime = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'ev68r_finder_types'

class Ev68RFooblaUvAccount(models.Model):
    id = models.IntegerField(primary_key=True)
    subdomain = models.CharField(max_length=255)
    published = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'ev68r_foobla_uv_account'

class Ev68RFooblaUvComment(models.Model):
    id = models.IntegerField(primary_key=True)
    idea_id = models.IntegerField()
    user_id = models.IntegerField()
    comment = models.TextField()
    createdate = models.DateTimeField()
    forum_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_foobla_uv_comment'

class Ev68RFooblaUvConfig(models.Model):
    id = models.IntegerField(primary_key=True)
    bad_word = models.TextField()
    listbox = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_foobla_uv_config'

class Ev68RFooblaUvDatetimeConfig(models.Model):
    id = models.IntegerField(primary_key=True)
    value = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True)
    default = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_foobla_uv_datetime_config'

class Ev68RFooblaUvForum(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=255)
    wellcome_message = models.CharField(max_length=255)
    prompt = models.CharField(max_length=255)
    example = models.CharField(max_length=255)
    default = models.IntegerField()
    published = models.IntegerField()
    limit_idea_page = models.IntegerField()
    limitpoint = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_foobla_uv_forum'

class Ev68RFooblaUvForumArticle(models.Model):
    forum_id = models.IntegerField()
    article_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_foobla_uv_forum_article'

class Ev68RFooblaUvGconfig(models.Model):
    key = models.CharField(primary_key=True, max_length=100)
    value = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'ev68r_foobla_uv_gconfig'

class Ev68RFooblaUvIdea(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=60, blank=True)
    content = models.TextField(blank=True)
    user_id = models.IntegerField()
    createdate = models.DateTimeField(blank=True, null=True)
    response = models.TextField(blank=True)
    resource = models.CharField(max_length=255)
    status_id = models.IntegerField()
    forum_id = models.IntegerField()
    votes = models.IntegerField(blank=True, null=True)
    published = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_foobla_uv_idea'

class Ev68RFooblaUvPermission(models.Model):
    group_id = models.IntegerField()
    new_idea_a = models.IntegerField()
    new_idea_o = models.IntegerField()
    edit_idea_a = models.IntegerField()
    edit_idea_o = models.IntegerField()
    delete_idea_a = models.IntegerField()
    delete_idea_o = models.IntegerField()
    change_status_a = models.IntegerField()
    change_status_o = models.IntegerField()
    vote_idea_a = models.IntegerField()
    vote_idea_o = models.IntegerField()
    response_idea_a = models.IntegerField()
    response_idea_o = models.IntegerField()
    new_comment_a = models.IntegerField()
    new_comment_o = models.IntegerField()
    edit_comment_a = models.IntegerField()
    edit_comment_o = models.IntegerField()
    delete_comment_a = models.IntegerField()
    delete_comment_o = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_foobla_uv_permission'

class Ev68RFooblaUvStatus(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100)
    parent_id = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'ev68r_foobla_uv_status'

class Ev68RFooblaUvTab(models.Model):
    status_id = models.IntegerField()
    forum_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_foobla_uv_tab'

class Ev68RFooblaUvVote(models.Model):
    idea_id = models.IntegerField()
    user_id = models.IntegerField()
    vote = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'ev68r_foobla_uv_vote'

class Ev68RFooblaUvVotesValue(models.Model):
    id = models.IntegerField(primary_key=True)
    vote_value = models.IntegerField()
    title = models.CharField(max_length=50, blank=True)
    published = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'ev68r_foobla_uv_votes_value'

class Ev68RHsconfig(models.Model):
    id = models.IntegerField(primary_key=True)
    css = models.TextField()
    script = models.TextField()
    overlayhtml = models.TextField()
    skincontrols = models.TextField()
    skincontent = models.TextField()
    params = models.TextField()
    published = models.IntegerField()
    modified = models.DateTimeField()
    publish_tmst = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'ev68r_hsconfig'

class Ev68RHwdvidsantileech(models.Model):
    index = models.IntegerField(primary_key=True)
    expiration = models.CharField(max_length=32)
    count = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_hwdvidsantileech'

class Ev68RHwdvidscategories(models.Model):
    id = models.IntegerField(primary_key=True)
    parent = models.IntegerField()
    category_name = models.CharField(max_length=250, blank=True)
    category_description = models.TextField(blank=True)
    date = models.DateTimeField()
    access_b_v = models.IntegerField()
    access_u_r = models.CharField(max_length=7)
    access_v_r = models.CharField(max_length=7)
    access_u = models.IntegerField()
    access_lev_u = models.CharField(max_length=250)
    access_v = models.IntegerField()
    access_lev_v = models.CharField(max_length=250)
    thumbnail = models.TextField()
    num_vids = models.IntegerField()
    num_subcats = models.IntegerField()
    order_by = models.CharField(max_length=15)
    ordering = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    published = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_hwdvidscategories'

class Ev68RHwdvidschannels(models.Model):
    id = models.IntegerField(primary_key=True)
    channel_name = models.TextField(blank=True)
    channel_description = models.TextField(blank=True)
    channel_thumbnail = models.TextField()
    public_private = models.CharField(max_length=250)
    date_created = models.DateTimeField()
    date_modified = models.DateTimeField()
    user_id = models.IntegerField(blank=True, null=True)
    views = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    featured = models.IntegerField()
    published = models.IntegerField()
    params = models.TextField()
    class Meta:
        managed = False
        db_table = 'ev68r_hwdvidschannels'

class Ev68RHwdvidsfavorites(models.Model):
    id = models.IntegerField(primary_key=True)
    userid = models.IntegerField(blank=True, null=True)
    videoid = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'ev68r_hwdvidsfavorites'

class Ev68RHwdvidsflaggedGroups(models.Model):
    id = models.IntegerField(primary_key=True)
    userid = models.IntegerField(blank=True, null=True)
    groupid = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=250)
    ignore = models.IntegerField()
    date = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'ev68r_hwdvidsflagged_groups'

class Ev68RHwdvidsflaggedVideos(models.Model):
    id = models.IntegerField(primary_key=True)
    userid = models.IntegerField(blank=True, null=True)
    videoid = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=250)
    ignore = models.IntegerField()
    date = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'ev68r_hwdvidsflagged_videos'

class Ev68RHwdvidsgroupMembership(models.Model):
    id = models.IntegerField(primary_key=True)
    memberid = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField()
    groupid = models.IntegerField(blank=True, null=True)
    approved = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_hwdvidsgroup_membership'

class Ev68RHwdvidsgroupVideos(models.Model):
    id = models.IntegerField(primary_key=True)
    videoid = models.IntegerField(blank=True, null=True)
    groupid = models.IntegerField(blank=True, null=True)
    memberid = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField()
    published = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_hwdvidsgroup_videos'

class Ev68RHwdvidsgroups(models.Model):
    id = models.IntegerField(primary_key=True)
    group_name = models.TextField(blank=True)
    public_private = models.CharField(max_length=250)
    date = models.DateTimeField()
    allow_comments = models.IntegerField()
    require_approval = models.IntegerField()
    group_description = models.TextField(blank=True)
    featured = models.IntegerField()
    adminid = models.IntegerField(blank=True, null=True)
    thumbnail = models.TextField()
    total_members = models.IntegerField(blank=True, null=True)
    total_videos = models.IntegerField(blank=True, null=True)
    ordering = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    published = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_hwdvidsgroups'

class Ev68RHwdvidsgs(models.Model):
    id = models.IntegerField(primary_key=True)
    setting = models.CharField(max_length=250, blank=True)
    value = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'ev68r_hwdvidsgs'

class Ev68RHwdvidslogsArchive(models.Model):
    id = models.IntegerField(primary_key=True)
    videoid = models.CharField(max_length=250, blank=True)
    views = models.IntegerField()
    number_of_votes = models.IntegerField()
    sum_of_votes = models.IntegerField()
    rating = models.IntegerField()
    favours = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_hwdvidslogs_archive'

class Ev68RHwdvidslogsFavours(models.Model):
    id = models.IntegerField(primary_key=True)
    videoid = models.IntegerField()
    userid = models.IntegerField()
    favour = models.IntegerField()
    date = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'ev68r_hwdvidslogs_favours'

class Ev68RHwdvidslogsViews(models.Model):
    id = models.IntegerField(primary_key=True)
    videoid = models.IntegerField()
    userid = models.IntegerField()
    date = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'ev68r_hwdvidslogs_views'

class Ev68RHwdvidslogsVotes(models.Model):
    id = models.IntegerField(primary_key=True)
    videoid = models.IntegerField()
    userid = models.IntegerField()
    vote = models.IntegerField()
    date = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'ev68r_hwdvidslogs_votes'

class Ev68RHwdvidsplaylists(models.Model):
    id = models.IntegerField(primary_key=True)
    playlist_name = models.TextField(blank=True)
    playlist_description = models.TextField(blank=True)
    playlist_data = models.TextField(blank=True)
    public_private = models.CharField(max_length=250)
    date_created = models.DateTimeField()
    date_modified = models.DateTimeField()
    allow_comments = models.IntegerField()
    user_id = models.IntegerField(blank=True, null=True)
    thumbnail = models.TextField()
    total_videos = models.IntegerField(blank=True, null=True)
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    featured = models.IntegerField()
    published = models.IntegerField()
    params = models.TextField()
    class Meta:
        managed = False
        db_table = 'ev68r_hwdvidsplaylists'

class Ev68RHwdvidsrating(models.Model):
    id = models.IntegerField(primary_key=True)
    userid = models.IntegerField(blank=True, null=True)
    videoid = models.IntegerField(blank=True, null=True)
    ip = models.CharField(max_length=15)
    date = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'ev68r_hwdvidsrating'

class Ev68RHwdvidsss(models.Model):
    id = models.IntegerField(primary_key=True)
    setting = models.CharField(max_length=250, blank=True)
    value = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'ev68r_hwdvidsss'

class Ev68RHwdvidssubs(models.Model):
    id = models.IntegerField(primary_key=True)
    userid = models.IntegerField()
    memberid = models.IntegerField()
    date = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'ev68r_hwdvidssubs'

class Ev68RHwdvidsvideoCategory(models.Model):
    videoid = models.IntegerField()
    categoryid = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_hwdvidsvideo_category'

class Ev68RHwdvidsvideos(models.Model):
    id = models.IntegerField(primary_key=True)
    video_type = models.CharField(max_length=250, blank=True)
    video_id = models.TextField(blank=True)
    title = models.TextField(blank=True)
    description = models.TextField(blank=True)
    tags = models.TextField(blank=True)
    category_id = models.IntegerField(blank=True, null=True)
    date_uploaded = models.DateTimeField()
    video_length = models.CharField(max_length=250, blank=True)
    allow_comments = models.IntegerField()
    allow_embedding = models.IntegerField()
    allow_ratings = models.IntegerField()
    rating_number_votes = models.IntegerField(blank=True, null=True)
    rating_total_points = models.IntegerField(blank=True, null=True)
    updated_rating = models.FloatField(blank=True, null=True)
    public_private = models.CharField(max_length=250, blank=True)
    thumb_snap = models.CharField(max_length=7, blank=True)
    thumbnail = models.TextField()
    approved = models.CharField(max_length=250, blank=True)
    number_of_views = models.IntegerField(blank=True, null=True)
    number_of_comments = models.IntegerField(blank=True, null=True)
    age_check = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    password = models.CharField(max_length=100)
    featured = models.IntegerField()
    ordering = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    published = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_hwdvidsvideos'

class Ev68RIgallery(models.Model):
    id = models.IntegerField(primary_key=True)
    ordering = models.IntegerField()
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    profile = models.IntegerField()
    parent = models.IntegerField()
    menu_image_filename = models.CharField(max_length=255)
    menu_description = models.TextField()
    gallery_description = models.TextField()
    user = models.IntegerField()
    published = models.IntegerField()
    date = models.DateTimeField()
    hits = models.IntegerField()
    publish_up = models.DateTimeField()
    publish_down = models.DateTimeField()
    moderate = models.IntegerField()
    competition_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_igallery'

class Ev68RIgalleryImg(models.Model):
    id = models.IntegerField(primary_key=True)
    gallery_id = models.IntegerField()
    ordering = models.IntegerField()
    date = models.DateTimeField()
    filename = models.CharField(max_length=255)
    description = models.TextField()
    tags = models.TextField()
    alt_text = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    target_blank = models.IntegerField()
    user = models.IntegerField()
    access = models.IntegerField()
    published = models.IntegerField()
    rotation = models.IntegerField()
    hits = models.IntegerField()
    menu_image = models.IntegerField()
    publish_up = models.DateTimeField()
    publish_down = models.DateTimeField()
    moderate = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_igallery_img'

class Ev68RIgalleryProfiles(models.Model):
    id = models.IntegerField(primary_key=True)
    ordering = models.IntegerField()
    name = models.CharField(max_length=255)
    img_quality = models.IntegerField()
    published = models.IntegerField()
    menu_max_width = models.IntegerField()
    menu_max_height = models.IntegerField()
    columns = models.IntegerField()
    show_large_image = models.IntegerField()
    max_width = models.IntegerField()
    max_height = models.IntegerField()
    img_container_width = models.IntegerField()
    img_container_height = models.IntegerField()
    fade_duration = models.IntegerField()
    preload = models.IntegerField()
    magnify = models.IntegerField()
    show_thumbs = models.IntegerField()
    thumb_width = models.IntegerField()
    thumb_height = models.IntegerField()
    crop_thumbs = models.IntegerField()
    thumb_position = models.CharField(max_length=10)
    thumb_container_width = models.IntegerField()
    thumb_container_height = models.IntegerField()
    images_per_row = models.IntegerField()
    thumb_scrollbar = models.IntegerField()
    arrows_up_down = models.IntegerField()
    arrows_left_right = models.IntegerField()
    scroll_speed = models.DecimalField(max_digits=2, decimal_places=2)
    scroll_boundary = models.IntegerField()
    gallery_des_position = models.CharField(max_length=10)
    allow_comments = models.IntegerField()
    allow_rating = models.IntegerField()
    align = models.CharField(max_length=10)
    style = models.CharField(max_length=64)
    show_slideshow_controls = models.IntegerField()
    slideshow_autostart = models.IntegerField()
    slideshow_pause = models.IntegerField()
    show_descriptions = models.IntegerField()
    photo_des_position = models.CharField(max_length=10)
    photo_des_width = models.IntegerField()
    photo_des_height = models.IntegerField()
    lightbox = models.IntegerField()
    lbox_max_width = models.IntegerField()
    lbox_max_height = models.IntegerField()
    lbox_img_container_width = models.IntegerField()
    lbox_img_container_height = models.IntegerField()
    lbox_fade_duration = models.IntegerField()
    lbox_preload = models.IntegerField()
    lbox_show_thumbs = models.IntegerField()
    lbox_thumb_width = models.IntegerField()
    lbox_thumb_height = models.IntegerField()
    lbox_crop_thumbs = models.IntegerField()
    lbox_thumb_position = models.CharField(max_length=12)
    lbox_thumb_container_width = models.IntegerField()
    lbox_thumb_container_height = models.IntegerField()
    lbox_images_per_row = models.IntegerField()
    lbox_thumb_scrollbar = models.IntegerField()
    lbox_arrows_left_right = models.IntegerField()
    lbox_arrows_up_down = models.IntegerField()
    lbox_scroll_speed = models.DecimalField(max_digits=2, decimal_places=2)
    lbox_scroll_boundary = models.IntegerField()
    lbox_allow_comments = models.IntegerField()
    lbox_allow_rating = models.IntegerField()
    lbox_close_position = models.CharField(max_length=12)
    lbox_show_slideshow_controls = models.IntegerField()
    lbox_slideshow_autostart = models.IntegerField()
    lbox_slideshow_pause = models.IntegerField()
    lbox_show_descriptions = models.IntegerField()
    lbox_photo_des_position = models.CharField(max_length=10)
    lbox_photo_des_width = models.IntegerField()
    lbox_photo_des_height = models.IntegerField()
    watermark = models.IntegerField()
    watermark_position = models.CharField(max_length=16)
    watermark_transparency = models.IntegerField()
    watermark_filename = models.CharField(max_length=255)
    download_image = models.CharField(max_length=16)
    lbox_download_image = models.CharField(max_length=16)
    show_search = models.IntegerField()
    show_cat_title = models.IntegerField()
    crop_menu = models.IntegerField()
    crop_main = models.IntegerField()
    crop_lbox = models.IntegerField()
    menu_pagination = models.IntegerField()
    menu_pagination_amount = models.IntegerField()
    round_large = models.IntegerField()
    round_thumb = models.IntegerField()
    round_fill = models.CharField(max_length=16)
    round_menu = models.IntegerField()
    refresh_mode = models.CharField(max_length=24)
    show_tags = models.IntegerField()
    lbox_show_tags = models.IntegerField()
    watermark_text = models.CharField(max_length=255)
    watermark_text_color = models.CharField(max_length=24)
    watermark_text_size = models.IntegerField()
    share_facebook = models.IntegerField()
    lbox_share_facebook = models.IntegerField()
    menu_image_defaults = models.IntegerField()
    report_image = models.IntegerField()
    lbox_report_image = models.IntegerField()
    thumb_pagination = models.IntegerField()
    thumb_pagination_amount = models.IntegerField()
    lbox_scalable = models.IntegerField()
    access = models.IntegerField()
    menu_access = models.IntegerField()
    show_category_hits = models.IntegerField()
    search_results = models.CharField(max_length=24)
    asset_id = models.IntegerField()
    slideshow_position = models.CharField(max_length=24)
    lbox_slideshow_position = models.CharField(max_length=24)
    show_filename = models.CharField(max_length=24)
    lbox_show_filename = models.CharField(max_length=24)
    show_numbering = models.IntegerField()
    lbox_show_numbering = models.IntegerField()
    show_thumb_info = models.CharField(max_length=24)
    lbox_show_thumb_info = models.CharField(max_length=24)
    plus_one = models.IntegerField()
    lbox_plus_one = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_igallery_profiles'

class Ev68RJaemLog(models.Model):
    id = models.IntegerField(primary_key=True)
    ext_id = models.CharField(unique=True, max_length=50, blank=True)
    service_id = models.IntegerField(blank=True, null=True)
    check_date = models.DateTimeField(blank=True, null=True)
    check_info = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'ev68r_jaem_log'

class Ev68RJaemServices(models.Model):
    id = models.IntegerField(primary_key=True)
    ws_name = models.CharField(max_length=255)
    ws_mode = models.CharField(max_length=50)
    ws_uri = models.CharField(max_length=255)
    ws_user = models.CharField(max_length=100)
    ws_pass = models.CharField(max_length=100)
    ws_default = models.IntegerField()
    ws_core = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_jaem_services'

class Ev68RJarpxMapid(models.Model):
    user_id = models.IntegerField()
    rpxid = models.CharField(max_length=50)
    class Meta:
        managed = False
        db_table = 'ev68r_jarpx_mapid'

class Ev68RJcomments(models.Model):
    id = models.IntegerField(primary_key=True)
    parent = models.IntegerField()
    thread_id = models.IntegerField()
    path = models.CharField(max_length=255)
    level = models.IntegerField()
    object_id = models.IntegerField()
    object_group = models.CharField(max_length=255)
    object_params = models.TextField()
    lang = models.CharField(max_length=255)
    userid = models.IntegerField()
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    homepage = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    comment = models.TextField()
    ip = models.CharField(max_length=39)
    date = models.DateTimeField()
    isgood = models.IntegerField()
    ispoor = models.IntegerField()
    published = models.IntegerField()
    deleted = models.IntegerField()
    subscribe = models.IntegerField()
    source = models.CharField(max_length=255)
    source_id = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    editor = models.CharField(max_length=50, blank=True)
    class Meta:
        managed = False
        db_table = 'ev68r_jcomments'

class Ev68RJcommentsBlacklist(models.Model):
    id = models.IntegerField(primary_key=True)
    ip = models.CharField(max_length=39)
    userid = models.IntegerField()
    created = models.DateTimeField()
    created_by = models.IntegerField()
    expire = models.DateTimeField()
    reason = models.TextField()
    notes = models.TextField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    editor = models.CharField(max_length=50, blank=True)
    class Meta:
        managed = False
        db_table = 'ev68r_jcomments_blacklist'

class Ev68RJcommentsCustomBbcodes(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)
    simple_pattern = models.CharField(max_length=255)
    simple_replacement_html = models.TextField()
    simple_replacement_text = models.TextField()
    pattern = models.CharField(max_length=255)
    replacement_html = models.TextField()
    replacement_text = models.TextField()
    button_acl = models.TextField()
    button_open_tag = models.CharField(max_length=16)
    button_close_tag = models.CharField(max_length=16)
    button_title = models.CharField(max_length=255)
    button_prompt = models.CharField(max_length=255)
    button_image = models.CharField(max_length=255)
    button_css = models.CharField(max_length=255)
    button_enabled = models.IntegerField()
    ordering = models.IntegerField()
    published = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_jcomments_custom_bbcodes'

class Ev68RJcommentsObjects(models.Model):
    id = models.IntegerField(primary_key=True)
    object_id = models.IntegerField()
    object_group = models.CharField(max_length=255)
    lang = models.CharField(max_length=20)
    title = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    access = models.IntegerField()
    userid = models.IntegerField()
    expired = models.IntegerField()
    modified = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'ev68r_jcomments_objects'

class Ev68RJcommentsReports(models.Model):
    id = models.IntegerField(primary_key=True)
    commentid = models.IntegerField()
    userid = models.IntegerField()
    name = models.CharField(max_length=255)
    ip = models.CharField(max_length=39)
    date = models.DateTimeField()
    reason = models.TextField()
    status = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_jcomments_reports'

class Ev68RJcommentsSettings(models.Model):
    component = models.CharField(max_length=50)
    lang = models.CharField(max_length=20)
    name = models.CharField(max_length=50)
    value = models.TextField()
    class Meta:
        managed = False
        db_table = 'ev68r_jcomments_settings'

class Ev68RJcommentsSubscriptions(models.Model):
    id = models.IntegerField(primary_key=True)
    object_id = models.IntegerField()
    object_group = models.CharField(max_length=255)
    lang = models.CharField(max_length=255)
    userid = models.IntegerField()
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    hash = models.CharField(max_length=255)
    published = models.IntegerField()
    source = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'ev68r_jcomments_subscriptions'

class Ev68RJcommentsVersion(models.Model):
    version = models.CharField(primary_key=True, max_length=16)
    previous = models.CharField(max_length=16)
    installed = models.DateTimeField()
    updated = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'ev68r_jcomments_version'

class Ev68RJcommentsVotes(models.Model):
    id = models.IntegerField(primary_key=True)
    commentid = models.IntegerField()
    userid = models.IntegerField()
    ip = models.CharField(max_length=39)
    date = models.DateTimeField()
    value = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_jcomments_votes'

class Ev68RLanguages(models.Model):
    lang_id = models.IntegerField(primary_key=True)
    lang_code = models.CharField(unique=True, max_length=7)
    title = models.CharField(max_length=50)
    title_native = models.CharField(max_length=50)
    sef = models.CharField(unique=True, max_length=50)
    image = models.CharField(unique=True, max_length=50)
    description = models.CharField(max_length=512)
    metakey = models.TextField()
    metadesc = models.TextField()
    sitename = models.CharField(max_length=1024)
    published = models.IntegerField()
    access = models.IntegerField()
    ordering = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_languages'

class Ev68RMenu(models.Model):
    id = models.IntegerField(primary_key=True)
    menutype = models.CharField(max_length=24)
    title = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    note = models.CharField(max_length=255)
    path = models.CharField(max_length=1024)
    link = models.CharField(max_length=1024)
    type = models.CharField(max_length=16)
    published = models.IntegerField()
    parent_id = models.IntegerField()
    level = models.IntegerField()
    component_id = models.IntegerField()
    ordering = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    browsernav = models.IntegerField(db_column='browserNav') # Field name made lowercase.
    access = models.IntegerField(blank=True, null=True)
    img = models.CharField(max_length=255)
    template_style_id = models.IntegerField()
    params = models.TextField()
    lft = models.IntegerField()
    rgt = models.IntegerField()
    home = models.IntegerField()
    language = models.CharField(max_length=7)
    client_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_menu'

class Ev68RMenuTypes(models.Model):
    id = models.IntegerField(primary_key=True)
    menutype = models.CharField(unique=True, max_length=24)
    title = models.CharField(max_length=48)
    description = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'ev68r_menu_types'

class Ev68RMessages(models.Model):
    message_id = models.IntegerField(primary_key=True)
    user_id_from = models.IntegerField()
    user_id_to = models.IntegerField()
    folder_id = models.IntegerField()
    date_time = models.DateTimeField()
    state = models.IntegerField()
    priority = models.IntegerField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    class Meta:
        managed = False
        db_table = 'ev68r_messages'

class Ev68RMessagesCfg(models.Model):
    user_id = models.IntegerField()
    cfg_name = models.CharField(max_length=100)
    cfg_value = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'ev68r_messages_cfg'

class Ev68RModules(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100)
    note = models.CharField(max_length=255)
    content = models.TextField()
    ordering = models.IntegerField()
    position = models.CharField(max_length=50)
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    publish_up = models.DateTimeField()
    publish_down = models.DateTimeField()
    published = models.IntegerField()
    module = models.CharField(max_length=50, blank=True)
    access = models.IntegerField(blank=True, null=True)
    showtitle = models.IntegerField()
    params = models.TextField()
    client_id = models.IntegerField()
    language = models.CharField(max_length=7)
    class Meta:
        managed = False
        db_table = 'ev68r_modules'

class Ev68RModulesMenu(models.Model):
    moduleid = models.IntegerField()
    menuid = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_modules_menu'

class Ev68RNewsfeeds(models.Model):
    catid = models.IntegerField()
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    alias = models.CharField(max_length=255)
    link = models.CharField(max_length=200)
    filename = models.CharField(max_length=200, blank=True)
    published = models.IntegerField()
    numarticles = models.IntegerField()
    cache_time = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    ordering = models.IntegerField()
    rtl = models.IntegerField()
    access = models.IntegerField(blank=True, null=True)
    language = models.CharField(max_length=7)
    params = models.TextField()
    created = models.DateTimeField()
    created_by = models.IntegerField()
    created_by_alias = models.CharField(max_length=255)
    modified = models.DateTimeField()
    modified_by = models.IntegerField()
    metakey = models.TextField()
    metadesc = models.TextField()
    metadata = models.TextField()
    xreference = models.CharField(max_length=50)
    publish_up = models.DateTimeField()
    publish_down = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'ev68r_newsfeeds'

class Ev68ROfflajnSlide(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=150)
    content = models.TextField()
    caption = models.TextField()
    ordering = models.IntegerField()
    groupprev = models.IntegerField()
    icon = models.CharField(max_length=255)
    slider = models.IntegerField()
    published = models.IntegerField()
    created = models.DateTimeField()
    created_by = models.IntegerField()
    created_by_alias = models.CharField(max_length=255)
    modified = models.DateTimeField()
    modified_by = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    publish_up = models.DateTimeField()
    publish_down = models.DateTimeField()
    params = models.TextField()
    access = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_offlajn_slide'

class Ev68ROfflajnSlider(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=150)
    type = models.CharField(max_length=100)
    theme = models.CharField(max_length=100)
    published = models.IntegerField()
    created = models.DateTimeField()
    created_by = models.IntegerField()
    created_by_alias = models.CharField(max_length=255)
    modified = models.DateTimeField()
    modified_by = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    publish_up = models.DateTimeField()
    publish_down = models.DateTimeField()
    params = models.TextField()
    access = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_offlajn_slider'

class Ev68ROverrider(models.Model):
    id = models.IntegerField(primary_key=True)
    constant = models.CharField(max_length=255)
    string = models.TextField()
    file = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'ev68r_overrider'

class Ev68RPopulateConf(models.Model):
    id = models.IntegerField(primary_key=True)
    skipfiles = models.TextField(blank=True)
    dmdescription = models.TextField()
    published = models.IntegerField()
    approved = models.IntegerField()
    dmthumbnail = models.CharField(max_length=255, blank=True)
    dmlicense_id = models.IntegerField(blank=True, null=True)
    dmlicense_display = models.IntegerField()
    dmmantainedby = models.IntegerField(blank=True, null=True)
    dmlastupdateby = models.IntegerField(blank=True, null=True)
    dmsubmitedby = models.IntegerField(blank=True, null=True)
    dmowner = models.IntegerField(blank=True, null=True)
    dmurl = models.CharField(max_length=255, blank=True)
    access = models.IntegerField()
    attribs = models.TextField()
    stripextension = models.IntegerField()
    orphansonly = models.IntegerField()
    nicetitle = models.IntegerField()
    password = models.CharField(max_length=255, blank=True)
    catid = models.IntegerField()
    usefiletime = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_populate_conf'

class Ev68RRedirectLinks(models.Model):
    id = models.IntegerField(primary_key=True)
    old_url = models.CharField(unique=True, max_length=255, blank=True)
    new_url = models.CharField(max_length=255, blank=True)
    referer = models.CharField(max_length=150)
    comment = models.CharField(max_length=255)
    hits = models.IntegerField()
    published = models.IntegerField()
    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'ev68r_redirect_links'

class Ev68RSchemas(models.Model):
    extension_id = models.IntegerField()
    version_id = models.CharField(max_length=20)
    class Meta:
        managed = False
        db_table = 'ev68r_schemas'

class Ev68RSession(models.Model):
    session_id = models.CharField(primary_key=True, max_length=200)
    client_id = models.IntegerField()
    guest = models.IntegerField(blank=True, null=True)
    time = models.CharField(max_length=14, blank=True)
    data = models.TextField(blank=True)
    userid = models.IntegerField(blank=True, null=True)
    username = models.CharField(max_length=150, blank=True)
    usertype = models.CharField(max_length=50, blank=True)
    class Meta:
        managed = False
        db_table = 'ev68r_session'

class Ev68RTemplateStyles(models.Model):
    id = models.IntegerField(primary_key=True)
    template = models.CharField(max_length=50)
    client_id = models.IntegerField()
    home = models.CharField(max_length=7)
    title = models.CharField(max_length=255)
    params = models.TextField()
    class Meta:
        managed = False
        db_table = 'ev68r_template_styles'

class Ev68RUpdateCategories(models.Model):
    categoryid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20, blank=True)
    description = models.TextField()
    parent = models.IntegerField(blank=True, null=True)
    updatesite = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'ev68r_update_categories'

class Ev68RUpdateSites(models.Model):
    update_site_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=20, blank=True)
    location = models.TextField()
    enabled = models.IntegerField(blank=True, null=True)
    last_check_timestamp = models.BigIntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'ev68r_update_sites'

class Ev68RUpdateSitesExtensions(models.Model):
    update_site_id = models.IntegerField()
    extension_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_update_sites_extensions'

class Ev68RUpdates(models.Model):
    update_id = models.IntegerField(primary_key=True)
    update_site_id = models.IntegerField(blank=True, null=True)
    extension_id = models.IntegerField(blank=True, null=True)
    categoryid = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    element = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=20, blank=True)
    folder = models.CharField(max_length=20, blank=True)
    client_id = models.IntegerField(blank=True, null=True)
    version = models.CharField(max_length=10, blank=True)
    data = models.TextField()
    detailsurl = models.TextField()
    infourl = models.TextField()
    class Meta:
        managed = False
        db_table = 'ev68r_updates'

class Ev68RUserNotes(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    catid = models.IntegerField()
    subject = models.CharField(max_length=100)
    body = models.TextField()
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    created_user_id = models.IntegerField()
    created_time = models.DateTimeField()
    modified_user_id = models.IntegerField()
    modified_time = models.DateTimeField()
    review_time = models.DateTimeField()
    publish_up = models.DateTimeField()
    publish_down = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'ev68r_user_notes'

class Ev68RUserProfiles(models.Model):
    user_id = models.IntegerField()
    profile_key = models.CharField(max_length=100)
    profile_value = models.CharField(max_length=255)
    ordering = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_user_profiles'

class Ev68RUserUsergroupMap(models.Model):
    user_id = models.IntegerField()
    group_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_user_usergroup_map'

class Ev68RUsergroups(models.Model):
    id = models.IntegerField(primary_key=True)
    parent_id = models.IntegerField()
    lft = models.IntegerField()
    rgt = models.IntegerField()
    title = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'ev68r_usergroups'

class Ev68RUsers(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=150)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    usertype = models.CharField(max_length=25)
    block = models.IntegerField()
    sendemail = models.IntegerField(db_column='sendEmail', blank=True, null=True) # Field name made lowercase.
    registerdate = models.DateTimeField(db_column='registerDate') # Field name made lowercase.
    lastvisitdate = models.DateTimeField(db_column='lastvisitDate') # Field name made lowercase.
    activation = models.CharField(max_length=100)
    params = models.TextField()
    lastresettime = models.DateTimeField(db_column='lastResetTime') # Field name made lowercase.
    resetcount = models.IntegerField(db_column='resetCount') # Field name made lowercase.

    additional = models.OneToOneField('legacy.Ev68RUsersAdditional', to_field='id', db_column='id')
    class Meta:
        managed = False
        db_table = 'ev68r_users'

class Ev68RUsersAdditional(models.Model):
    id = models.IntegerField(primary_key=True)

    velo_first_name = models.CharField(max_length=100)
    velo_last_name = models.CharField(max_length=100)
    velo_country = models.CharField(max_length=50)
    velo_ssn = models.CharField(max_length=30)
    velo_birthday = models.DateField()
    velo_city = models.CharField(max_length=50)
    velo_velo_name = models.CharField(max_length=50)
    velo_phone_number = models.CharField(max_length=50)
    velo_newsletter = models.IntegerField()
    velo_img = models.CharField(max_length=255)
    velo_draugiem_id = models.BigIntegerField()
    velo_draugiem_token = models.CharField(max_length=50)
    velo_draugiem_joined = models.DateTimeField()
    velo_fb_id = models.BigIntegerField()
    velo_fb_token = models.CharField(max_length=50)
    velo_fb_joined = models.DateTimeField()
    velo_fb_linked = models.IntegerField()
    velo_twitter_id = models.BigIntegerField()
    velo_twitter_login = models.CharField(max_length=50)
    velo_twitter_token = models.CharField(max_length=255)
    velo_twitter_joined = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'ev68r_users_additional'

class Ev68RVeloAliasFix(models.Model):
    id = models.IntegerField(primary_key=True)
    state = models.IntegerField()
    participant_first_name = models.CharField(max_length=100)
    participant_last_name = models.CharField(max_length=100)
    participant_birthday = models.DateField()
    participant_city = models.CharField(max_length=50)
    alias = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'ev68r_velo_alias_fix'

class Ev68RVeloApplications(models.Model):
    id = models.IntegerField(primary_key=True)
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    status = models.IntegerField()
    user_id = models.IntegerField()
    competition_id = models.IntegerField()
    created = models.DateTimeField()
    competition_id_complex = models.IntegerField()
    payment_id = models.IntegerField()
    email_sent = models.IntegerField()
    rnd = models.CharField(max_length=50)
    remainder_email = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_velo_applications'

class Ev68RVeloCompetitions(models.Model):
    id = models.IntegerField(primary_key=True)
    ordering = models.IntegerField()
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    title_lv_lv = models.CharField(db_column='title_lv-LV', max_length=255) # Field name made lowercase. Field renamed to remove unsuitable characters.
    alias = models.CharField(max_length=255)
    title_en_gb = models.CharField(db_column='title_en-GB', max_length=255) # Field name made lowercase. Field renamed to remove unsuitable characters.
    title_ru_ru = models.CharField(db_column='title_ru-RU', max_length=255) # Field name made lowercase. Field renamed to remove unsuitable characters.
    where = models.CharField(max_length=255)
    parent_id = models.IntegerField()
    competition_date = models.DateTimeField()
    competition_type = models.CharField(max_length=30)
    cid = models.IntegerField()
    menu_cid = models.IntegerField()
    complex_payments = models.IntegerField()
    complex_enddate = models.DateTimeField()
    complex_discount = models.IntegerField()
    level = models.IntegerField()
    lft = models.IntegerField()
    rgt = models.IntegerField()
    path = models.CharField(max_length=1024)
    applyimage = models.CharField(db_column='applyImage', max_length=255) # Field name made lowercase.
    params = models.TextField()
    billseries = models.CharField(db_column='billSeries', max_length=20) # Field name made lowercase.
    paymentchannelbig = models.CharField(db_column='paymentChannelBIG', max_length=20) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'ev68r_velo_competitions'

class Ev68RVeloCouponCodes(models.Model):
    id = models.IntegerField(primary_key=True)
    state = models.IntegerField()
    coupon_code = models.CharField(unique=True, max_length=50)
    created = models.DateTimeField()
    created_by = models.IntegerField()
    usage_times = models.IntegerField()
    usage_times_left = models.IntegerField()
    due_date = models.DateTimeField()
    discount_participation = models.CharField(max_length=10)
    discount_insurance = models.CharField(max_length=10)
    discount_products = models.CharField(max_length=10)
    product_id = models.IntegerField()
    params = models.CharField(max_length=1000)
    application = models.ForeignKey(Ev68RVeloApplications)
    class Meta:
        managed = False
        db_table = 'ev68r_velo_coupon_codes'

class Ev68RVeloDistance(models.Model):
    id = models.IntegerField(primary_key=True)
    ordering = models.IntegerField()
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    title_lv_lv = models.CharField(db_column='title_lv-LV', max_length=255) # Field name made lowercase. Field renamed to remove unsuitable characters.
    alias = models.CharField(max_length=255)
    title_en_gb = models.CharField(db_column='title_en-GB', max_length=255) # Field name made lowercase. Field renamed to remove unsuitable characters.
    title_ru_ru = models.CharField(db_column='title_ru-RU', max_length=255) # Field name made lowercase. Field renamed to remove unsuitable characters.
    competition_id = models.IntegerField()
    km = models.CharField(max_length=30)
    params = models.TextField()
    class Meta:
        managed = False
        db_table = 'ev68r_velo_distance'

class Ev68RVeloInsurance(models.Model):
    id = models.IntegerField(primary_key=True)
    ordering = models.IntegerField()
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    competition_id = models.IntegerField()
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    complex_discount = models.IntegerField()
    present = models.IntegerField()
    present_count = models.IntegerField()
    present_reserved = models.IntegerField()
    complex = models.IntegerField()
    params = models.TextField()
    class Meta:
        managed = False
        db_table = 'ev68r_velo_insurance'

class Ev68RVeloInsurancePresents(models.Model):
    id = models.IntegerField(primary_key=True)
    ordering = models.IntegerField()
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    application = models.ForeignKey(Ev68RVeloApplications)
    insurance_id = models.IntegerField()
    created = models.DateTimeField()
    payment_id = models.IntegerField()
    participation_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_velo_insurance_presents'

class Ev68RVeloInvoiceItems(models.Model):
    id = models.IntegerField(primary_key=True)
    ordering = models.IntegerField()
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    invoice_id = models.IntegerField()
    user_id = models.IntegerField()
    text = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    measurement = models.CharField(max_length=30)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    total_with_taxes = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_title = models.CharField(max_length=50)
    created = models.DateTimeField()
    created_by = models.IntegerField()
    updated = models.DateTimeField()
    updated_by = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_velo_invoice_items'

class Ev68RVeloInvoices(models.Model):
    id = models.IntegerField(primary_key=True)
    ordering = models.IntegerField()
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    user_id = models.IntegerField()
    bill_series = models.CharField(max_length=20)
    bill_nr = models.IntegerField()
    customer_type = models.CharField(max_length=10)
    customer = models.CharField(max_length=255)
    customer_country = models.CharField(max_length=50)
    customer_vat = models.CharField(max_length=255)
    customer_regnr = models.CharField(max_length=255)
    customer_address = models.CharField(max_length=255)
    customer_juridicaladdress = models.CharField(max_length=255)
    total_lvl = models.DecimalField(max_digits=10, decimal_places=2)
    total_euro = models.DecimalField(max_digits=10, decimal_places=2)
    comments = models.CharField(max_length=255)
    payday = models.DateField()
    currency_rate = models.DecimalField(max_digits=10, decimal_places=7)
    date = models.DateField()
    status = models.IntegerField()
    taxes_lvl = models.DecimalField(max_digits=10, decimal_places=2)
    taxes_euro = models.DecimalField(max_digits=10, decimal_places=2)
    total_without_taxes_lvl = models.DecimalField(max_digits=10, decimal_places=2)
    total_without_taxes_euro = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateTimeField()
    sender = models.CharField(max_length=255)
    sender_vat = models.CharField(max_length=255)
    sender_regnr = models.CharField(max_length=255)
    sender_address = models.CharField(max_length=255)
    sender_bank = models.CharField(max_length=255)
    sender_bank_code = models.CharField(max_length=255)
    sender_bank_number = models.CharField(max_length=255)
    total_lvl_txt = models.CharField(max_length=255)
    total_euro_txt = models.CharField(max_length=255)
    signature = models.CharField(max_length=255)
    vat_description = models.CharField(max_length=255)
    created_by = models.IntegerField()
    updated = models.DateTimeField()
    updated_by = models.IntegerField()
    docman_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_velo_invoices'

class Ev68RVeloLog(models.Model):
    id = models.IntegerField(primary_key=True)
    ordering = models.IntegerField()
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    user_id = models.IntegerField()
    log_type = models.CharField(max_length=50)
    level = models.CharField(max_length=30)
    code = models.CharField(max_length=255)
    debug_variables = models.TextField()
    source_code = models.TextField()
    date = models.DateTimeField()
    ip = models.CharField(max_length=50)
    username = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'ev68r_velo_log'

class Ev68RVeloParticipations(models.Model):
    id = models.IntegerField(primary_key=True)
    ordering = models.IntegerField()
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    competition_id = models.IntegerField()
    distance_id = models.IntegerField()
    price_id = models.IntegerField()
    user_id = models.IntegerField()
    team_id = models.IntegerField()
    created = models.DateTimeField()
    created_by = models.IntegerField()
    updated = models.DateTimeField()
    updated_by = models.IntegerField()
    status = models.IntegerField()
    insured = models.IntegerField()
    team_reserve = models.IntegerField()
    insurance_id = models.IntegerField()
    registerer_id = models.IntegerField()
    application = models.ForeignKey(Ev68RVeloApplications)
    tc_id = models.IntegerField()
    alias = models.CharField(max_length=210)
    participant_first_name = models.CharField(max_length=100)
    participant_last_name = models.CharField(max_length=100)
    participant_ssn = models.CharField(max_length=30)
    participant_birthday = models.DateField()
    participant_country = models.CharField(max_length=100)
    participant_city = models.CharField(max_length=50)
    participant_team_name = models.CharField(max_length=50)
    participant_velo_name = models.CharField(max_length=50)
    participant_phone_number = models.CharField(max_length=50)
    participant_phone_number_sms = models.IntegerField()
    participant_email = models.CharField(max_length=100)
    participant_email_newsletter = models.IntegerField()
    participant_where = models.CharField(max_length=30)
    participant_occupation = models.CharField(max_length=30)
    email_sent = models.IntegerField()
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    dzimums = models.CharField(max_length=1)
    class Meta:
        managed = False
        db_table = 'ev68r_velo_participations'

class Ev68RVeloPayments(models.Model):
    id = models.IntegerField(primary_key=True)
    ordering = models.IntegerField()
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    user_id = models.IntegerField()
    application = models.ForeignKey(Ev68RVeloApplications)
    invoice_id = models.IntegerField()
    team_id = models.IntegerField()
    coupon_id = models.IntegerField()
    total_person_lvl = models.DecimalField(max_digits=10, decimal_places=2)
    total_insurance_lvl = models.DecimalField(max_digits=10, decimal_places=2)
    total_addons_lvl = models.DecimalField(max_digits=10, decimal_places=2)
    total_lvl = models.DecimalField(max_digits=10, decimal_places=2)
    complex_payment = models.IntegerField()
    payment_channel = models.CharField(max_length=30)
    accept_terms = models.IntegerField()
    accept_insurance_terms = models.IntegerField()
    accept_terms_inform_others = models.IntegerField()
    paymentchannelbig = models.CharField(db_column='paymentChannelBIG', max_length=20, blank=True) # Field name made lowercase.
    code = models.CharField(max_length=45, blank=True)
    erekins_status = models.IntegerField(blank=True, null=True)
    email_sent = models.IntegerField(blank=True, null=True)
    random_id = models.CharField(unique=True, max_length=50, blank=True)
    class Meta:
        managed = False
        db_table = 'ev68r_velo_payments'

class Ev68RVeloPaymentsTransactions(models.Model):
    id = models.IntegerField(primary_key=True)
    ordering = models.IntegerField()
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    transaction_id = models.CharField(max_length=50)
    payment_id = models.IntegerField()
    channel = models.CharField(max_length=255)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=20)
    referencenr = models.CharField(max_length=50)
    information = models.CharField(max_length=255)
    result = models.CharField(max_length=10)
    result_check = models.CharField(max_length=10)
    ip_address = models.CharField(max_length=16)
    server_ip_address = models.CharField(max_length=16)
    user_ip_address = models.CharField(max_length=16)
    language = models.CharField(max_length=7)
    client_name = models.CharField(max_length=255)
    client_account = models.CharField(max_length=255)
    executed_payment_total = models.DecimalField(max_digits=10, decimal_places=2)
    executed_payment_currency = models.CharField(max_length=20)
    executed_payment_name = models.CharField(max_length=255)
    executed_payment_bank_account = models.CharField(max_length=255)
    answer_user_datetime = models.DateTimeField()
    answer_server_datetime = models.DateTimeField()
    created = models.DateTimeField()
    updated = models.DateTimeField()
    email_sent = models.IntegerField()
    paymentchannelbig = models.CharField(db_column='paymentChannelBIG', max_length=20, blank=True) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'ev68r_velo_payments_transactions'

class Ev68RVeloPicklistValues(models.Model):
    id = models.IntegerField(primary_key=True)
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    picktype = models.CharField(db_column='pickType', max_length=30) # Field name made lowercase.
    value = models.CharField(max_length=30)
    class Meta:
        managed = False
        db_table = 'ev68r_velo_picklist_values'

class Ev68RVeloPrice(models.Model):
    id = models.IntegerField(primary_key=True)
    ordering = models.IntegerField()
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    competition_id = models.IntegerField()
    distance_id = models.IntegerField()
    from_year = models.IntegerField()
    till_year = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    start_registering = models.DateTimeField()
    end_registering = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'ev68r_velo_price'

class Ev68RVeloProductAttributes(models.Model):
    id = models.IntegerField(primary_key=True)
    ordering = models.IntegerField()
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    product_id = models.IntegerField()
    title_lv_lv = models.CharField(db_column='title_lv-LV', max_length=50) # Field name made lowercase. Field renamed to remove unsuitable characters.
    title_en_gb = models.CharField(db_column='title_en-GB', max_length=50) # Field name made lowercase. Field renamed to remove unsuitable characters.
    title_ru_ru = models.CharField(db_column='title_ru-RU', max_length=50) # Field name made lowercase. Field renamed to remove unsuitable characters.
    limit = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_velo_product_attributes'

class Ev68RVeloProducts(models.Model):
    id = models.IntegerField(primary_key=True)
    ordering = models.IntegerField()
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    competition_id = models.IntegerField()
    limit = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    title_lv_lv = models.CharField(db_column='title_lv-LV', max_length=50) # Field name made lowercase. Field renamed to remove unsuitable characters.
    title_en_gb = models.CharField(db_column='title_en-GB', max_length=50) # Field name made lowercase. Field renamed to remove unsuitable characters.
    title_ru_ru = models.CharField(db_column='title_ru-RU', max_length=50) # Field name made lowercase. Field renamed to remove unsuitable characters.
    type = models.CharField(max_length=50)
    description_lv_lv = models.TextField(db_column='description_lv-LV') # Field name made lowercase. Field renamed to remove unsuitable characters.
    description_en_gb = models.TextField(db_column='description_en-GB') # Field name made lowercase. Field renamed to remove unsuitable characters.
    description_ru_ru = models.TextField(db_column='description_ru-RU') # Field name made lowercase. Field renamed to remove unsuitable characters.
    params = models.TextField()
    complex_discount = models.IntegerField()
    complex_multiple = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_velo_products'

class Ev68RVeloProductsParticipations(models.Model):
    id = models.IntegerField(primary_key=True)
    ordering = models.IntegerField()
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    product_id = models.IntegerField()
    attribute_id = models.IntegerField()
    participation_id = models.IntegerField()
    value = models.CharField(max_length=50)
    class Meta:
        managed = False
        db_table = 'ev68r_velo_products_participations'

class Ev68RVeloResults(models.Model):
    id = models.IntegerField(primary_key=True)
    state = models.IntegerField()
    competition_id = models.IntegerField()
    distance_id = models.IntegerField()
    participation_id = models.IntegerField()
    new_participant = models.IntegerField()
    number = models.IntegerField()
    group = models.CharField(max_length=50)
    alias = models.CharField(max_length=210)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    year = models.IntegerField()
    team_name = models.CharField(max_length=100)
    velo = models.CharField(max_length=100)
    time = models.TimeField(blank=True, null=True)
    finish_seq = models.IntegerField()
    loses_group = models.TimeField(blank=True, null=True)
    length_meters = models.IntegerField()
    avg_speed = models.DecimalField(max_digits=4, decimal_places=2)
    loses_distance = models.TimeField(blank=True, null=True)
    result_group = models.IntegerField()
    result_distance = models.IntegerField()
    points_group = models.IntegerField()
    points_distance = models.IntegerField()
    status = models.CharField(max_length=50)
    diploma_url = models.CharField(max_length=50, blank=True)
    class Meta:
        managed = False
        db_table = 'ev68r_velo_results'

class Ev68RVeloResultsAwards(models.Model):
    id = models.IntegerField(primary_key=True)
    ordering = models.IntegerField()
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    competition_id = models.IntegerField()
    alias = models.CharField(max_length=210)
    title = models.CharField(max_length=255)
    logo = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'ev68r_velo_results_awards'

class Ev68RVeloResultsSebTotal(models.Model):
    id = models.IntegerField(primary_key=True)
    state = models.IntegerField()
    competition_id = models.IntegerField()
    distance_id = models.IntegerField()
    participation_id = models.IntegerField()
    group = models.CharField(max_length=50)
    number = models.IntegerField()
    alias = models.CharField(max_length=210)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    year = models.IntegerField()
    team_name = models.CharField(max_length=100)
    velo = models.CharField(max_length=100)
    g_p1 = models.IntegerField()
    g_p2 = models.IntegerField()
    g_p3 = models.IntegerField()
    g_p4 = models.IntegerField()
    g_p5 = models.IntegerField()
    g_p6 = models.IntegerField()
    g_p7 = models.IntegerField()
    g_total = models.IntegerField()
    g_place = models.IntegerField()
    d_p1 = models.IntegerField()
    d_p2 = models.IntegerField()
    d_p3 = models.IntegerField()
    d_p4 = models.IntegerField()
    d_p5 = models.IntegerField()
    d_p6 = models.IntegerField()
    d_p7 = models.IntegerField()
    d_place1 = models.IntegerField()
    d_place2 = models.IntegerField()
    d_place3 = models.IntegerField()
    d_place4 = models.IntegerField()
    d_place5 = models.IntegerField()
    d_place6 = models.IntegerField()
    d_place7 = models.IntegerField()
    d_total = models.IntegerField()
    d_place = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_velo_results_seb_total'

class Ev68RVeloSupporters(models.Model):
    id = models.IntegerField(primary_key=True)
    ordering = models.IntegerField()
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    title = models.CharField(max_length=255)
    sponsor_type = models.CharField(max_length=255)
    logo = models.CharField(max_length=255)
    description = models.TextField()
    url = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    title_ru = models.CharField(max_length=255)
    description_en = models.TextField()
    description_ru = models.TextField()
    agency_sponsor = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_velo_supporters'

class Ev68RVeloSupportersCompetitions(models.Model):
    id = models.IntegerField(primary_key=True)
    ordering = models.IntegerField()
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    supporter_id = models.IntegerField()
    competition_id = models.IntegerField()
    sponsor_type = models.CharField(max_length=50)
    class Meta:
        managed = False
        db_table = 'ev68r_velo_supporters_competitions'

class Ev68RVeloSupportersResults(models.Model):
    id = models.IntegerField(primary_key=True)
    ordering = models.IntegerField()
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    title = models.CharField(max_length=255)
    competition_id = models.IntegerField()
    logo = models.CharField(max_length=255)
    group_name = models.CharField(max_length=50)
    distance_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_velo_supporters_results'

class Ev68RVeloTeamMembers(models.Model):
    id = models.IntegerField(primary_key=True)
    team = models.ForeignKey('legacy.Ev68RVeloTeams')
    ordering = models.IntegerField()
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    # team_id = models.IntegerField()
    user_id = models.IntegerField()
    admin = models.IntegerField()
    participant = models.IntegerField()
    participant_first_name = models.CharField(max_length=100)
    participant_last_name = models.CharField(max_length=100)
    participant_ssn = models.CharField(max_length=30)
    participant_birthday = models.DateField()
    participant_country = models.CharField(max_length=100)
    created = models.DateTimeField()
    created_by = models.IntegerField()
    updated = models.DateTimeField()
    updated_by = models.IntegerField()
    payed_for_full_season = models.IntegerField()
    licence_nr = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'ev68r_velo_team_members'

class Ev68RVeloTeams(models.Model):
    id = models.IntegerField(primary_key=True)
    ordering = models.IntegerField()
    state = models.IntegerField()
    checked_out1 = models.IntegerField()
    checked_out_time1 = models.DateTimeField()
    title = models.CharField(max_length=50)
    description = models.TextField()
    image = models.CharField(max_length=255)
    shirt_image = models.CharField(max_length=255)
    country = models.CharField(max_length=50)
    person = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    management_info = models.TextField()
    type = models.CharField(max_length=255)
    featured = models.IntegerField()
    payment_id = models.IntegerField()
    status = models.IntegerField()
    created = models.DateTimeField()
    created_by = models.IntegerField()
    updated = models.DateTimeField()
    updated_by = models.IntegerField()
    competition_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_velo_teams'

class Ev68RVeloTeamsCompetitions(models.Model):
    id = models.IntegerField(primary_key=True)
    ordering = models.IntegerField()
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    # team_id = models.IntegerField()
    team = models.ForeignKey('legacy.Ev68RVeloTeams')
    member_id = models.IntegerField()
    competition_id = models.IntegerField()
    type = models.CharField(max_length=255)
    payment_id = models.IntegerField()
    status = models.IntegerField()
    created = models.DateTimeField()
    created_by = models.IntegerField()
    updated = models.DateTimeField()
    updated_by = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'ev68r_velo_teams_competitions'

class Ev68RViewlevels(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(unique=True, max_length=100)
    ordering = models.IntegerField()
    rules = models.CharField(max_length=5120)
    class Meta:
        managed = False
        db_table = 'ev68r_viewlevels'

class Ev68RWeblinks(models.Model):
    id = models.IntegerField(primary_key=True)
    catid = models.IntegerField()
    sid = models.IntegerField()
    title = models.CharField(max_length=250)
    alias = models.CharField(max_length=255)
    url = models.CharField(max_length=250)
    description = models.TextField()
    date = models.DateTimeField()
    hits = models.IntegerField()
    state = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    ordering = models.IntegerField()
    archived = models.IntegerField()
    approved = models.IntegerField()
    access = models.IntegerField()
    params = models.TextField()
    language = models.CharField(max_length=7)
    created = models.DateTimeField()
    created_by = models.IntegerField()
    created_by_alias = models.CharField(max_length=255)
    modified = models.DateTimeField()
    modified_by = models.IntegerField()
    metakey = models.TextField()
    metadesc = models.TextField()
    metadata = models.TextField()
    featured = models.IntegerField()
    xreference = models.CharField(max_length=50)
    publish_up = models.DateTimeField()
    publish_down = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'ev68r_weblinks'

class Ev68RWfProfiles(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    users = models.TextField()
    types = models.TextField(blank=True)
    components = models.TextField()
    area = models.IntegerField()
    device = models.CharField(max_length=255, blank=True)
    rows = models.TextField()
    plugins = models.TextField()
    published = models.IntegerField()
    ordering = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    params = models.TextField()
    class Meta:
        managed = False
        db_table = 'ev68r_wf_profiles'

