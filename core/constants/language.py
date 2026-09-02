"""
This web application uses ISO 639-1 for language codes,
as is common in enterprise multi-tenant applications,
assuming the language set covers most business needs.

Base on "https://developers.google.com/admin-sdk/directory/v1/languages"
some languages have `active = True`, meaning they are available
to the frontend and visible to users.
"""
from dataclasses import dataclass

from lingua import Language

from core.constants.base import GeneralConstant


"""
Language Proficiencies
"""
@dataclass(frozen=True)
class _LanguageProficiency(GeneralConstant):
  uid: int
  name: str
  level: int
  display_order: int


@dataclass(frozen=True)
class _LanguageProficiencies(GeneralConstant):
  ELEMENTARY: _LanguageProficiency = _LanguageProficiency(
    uid=1,
    name='Elementary proficiency',
    level=1,
    display_order=1,
  )
  LIMITED: _LanguageProficiency = _LanguageProficiency(
    uid=2,
    name='Limited working proficiency',
    level=2,
    display_order=2,
  )
  PROFESSIONAL: _LanguageProficiency = _LanguageProficiency(
    uid=3,
    name='Professional working proficiency',
    level=3,
    display_order=3,
  )
  FULL_PROFESSIONAL: _LanguageProficiency = _LanguageProficiency(
    uid=4,
    name='Full professional proficiency',
    level=4,
    display_order=4,
  )
  NATIVE: _LanguageProficiency = _LanguageProficiency(
    uid=5,
    name='Native or bilingual proficiency',
    level=5,
    display_order=5,
  )

  def get_uid_list(self):
    return [proficiency.uid for proficiency in self.as_list()]

  def get_max_languages(self):
    return 8

  def get_uids_with_level_gte(self, uid):
    level = None
    for proficiency in self.as_list():
      if proficiency.uid == uid:
        level = proficiency.level
        break

    if level is None:
      return []

    return [
      proficiency.uid for proficiency in self.as_list()\
      if proficiency.level >= level
    ]


LANGUAGE_PROFICIENCIES = _LanguageProficiencies()


"""
Language Code
"""
BCP_47_LANGUAGES = (
  {'code': 'am', 'display_name': 'Amharic', 'active': False},
  {
    'code': 'ar',
    'display_name': 'Arabic',
    'active': True,
    'lingua': Language.ARABIC,
  },
  {'code': 'az', 'display_name': 'Azerbaijani', 'active': False},
  {'code': 'bg', 'display_name': 'Bulgarian', 'active': False},
  {'code': 'bn', 'display_name': 'Bengali', 'active': False},
  {'code': 'bs', 'display_name': 'Bosnian', 'active': False},
  {'code': 'ca', 'display_name': 'Catalan', 'active': False},
  {'code': 'cs', 'display_name': 'Czech', 'active': False},
  {'code': 'da', 'display_name': 'Danish', 'active': False},
  {
    'code': 'de',
    'display_name': 'German',
    'active': True,
    'lingua': Language.GERMAN,
  },
  {'code': 'el', 'display_name': 'Greek', 'active': False},
  {
    'code': 'en',
    'display_name': 'English',
    'active': True,
    'lingua': Language.ENGLISH,
  },
  {
    'code': 'es-ES',
    'display_name': 'Spanish (Spain)',
    'active': True,
    'lingua': Language.SPANISH,
  },
  {
    'code': 'es-419',
    'display_name': 'Spanish (Latin America)',
    'active': True,
    'lingua': Language.SPANISH,
  },
  {'code': 'et', 'display_name': 'Estonian', 'active': False},
  {'code': 'eu', 'display_name': 'Basque', 'active': False},
  {'code': 'fa', 'display_name': 'Persian', 'active': False},
  {'code': 'fi', 'display_name': 'Finnish', 'active': False},
  {'code': 'fil', 'display_name': 'Filipino', 'active': False},
  {
    'code': 'fr',
    'display_name': 'French',
    'active': True,
    'lingua': Language.FRENCH,
  },
  {'code': 'he', 'display_name': 'Hebrew', 'active': False},
  {
    'code': 'hi',
    'display_name': 'Hindi',
    'active': True,
    'lingua': Language.HINDI,
  },
  {'code': 'hr', 'display_name': 'Croatian', 'active': False},
  {'code': 'hu', 'display_name': 'Hungarian', 'active': False},
  {
    'code': 'id',
    'display_name': 'Indonesian',
    'active': True,
    'lingua': Language.INDONESIAN,
  },
  {
    'code': 'it',
    'display_name': 'Italian',
    'active': True,
    'lingua': Language.ITALIAN,
  },
  {
    'code': 'ja',
    'display_name': 'Japanese',
    'active': True,
    'lingua': Language.JAPANESE,
  },
  {'code': 'ka', 'display_name': 'Georgian', 'active': False},
  {'code': 'kk', 'display_name': 'Kazakh', 'active': False},
  {
    'code': 'ko',
    'display_name': 'Korean',
    'active': True,
    'lingua': Language.KOREAN,
  },
  {'code': 'lt', 'display_name': 'Lithuanian', 'active': False},
  {'code': 'lv', 'display_name': 'Latvian', 'active': False},
  {'code': 'mk', 'display_name': 'Macedonian', 'active': False},
  {'code': 'ms', 'display_name': 'Malay', 'active': False},
  {
    'code': 'nl',
    'display_name': 'Dutch',
    'active': True,
    'lingua': Language.DUTCH,
  },
  {'code': 'nb', 'display_name': 'Norwegian Bokmål', 'active': False},
  {'code': 'pl', 'display_name': 'Polish', 'active': False},
  {
    'code': 'pt-BR',
    'display_name': 'Portuguese (Brazil)',
    'active': True,
    'lingua': Language.PORTUGUESE,
  },
  {
    'code': 'pt-PT',
    'display_name': 'Portuguese (Portugal)',
    'active': True,
    'lingua': Language.PORTUGUESE,
  },
  {'code': 'ro', 'display_name': 'Romanian', 'active': False},
  {
    'code': 'ru',
    'display_name': 'Russian',
    'active': False,
    'lingua': Language.RUSSIAN,
  },
  {'code': 'sk', 'display_name': 'Slovak', 'active': False},
  {'code': 'sl', 'display_name': 'Slovenian', 'active': False},
  {'code': 'sr', 'display_name': 'Serbian (Cyrillic)', 'active': False},
  {'code': 'sr-Latn', 'display_name': 'Serbian (Latin)', 'active': False},
  {'code': 'sv', 'display_name': 'Swedish', 'active': False},
  {'code': 'ta', 'display_name': 'Tamil', 'active': False},
  {'code': 'te', 'display_name': 'Telugu', 'active': False},
  {
    'code': 'th',
    'display_name': 'Thai',
    'active': True,
    'lingua': Language.THAI,
  },
  {
    'code': 'tr',
    'display_name': 'Turkish',
    'active': True,
    'lingua': Language.TURKISH,
  },
  {
    'code': 'uk',
    'display_name': 'Ukrainian',
    'active': False,
    'lingua': Language.UKRAINIAN,
  },
  {'code': 'ur', 'display_name': 'Urdu', 'active': False},
  {
    'code': 'vi',
    'display_name': 'Vietnamese',
    'active': True,
    'lingua': Language.VIETNAMESE,
  },
  {
    'code': 'zh-Hans',
    'display_name': 'Chinese (Simplified)',
    'active': True,
    'lingua': Language.CHINESE,
  },
  {
    'code': 'zh-Hant',
    'display_name': 'Chinese (Traditional)',
    'active': True,
    'lingua': Language.CHINESE,
  },
)

ISO_639_1 = (
  { 'code': 'ab', 'display_name': 'Abkhaz', 'active': False },
  { 'code': 'aa', 'display_name': 'Afar', 'active': False },
  { 'code': 'af', 'display_name': 'Afrikaans', 'active': False },
  { 'code': 'ak', 'display_name': 'Akan', 'active': False },
  { 'code': 'sq', 'display_name': 'Albanian', 'active': False },
  { 'code': 'am', 'display_name': 'Amharic', 'active': True },
  { 'code': 'ar', 'display_name': 'Arabic', 'active': True },
  { 'code': 'an', 'display_name': 'Aragonese', 'active': False },
  { 'code': 'hy', 'display_name': 'Armenian', 'active': False },
  { 'code': 'as', 'display_name': 'Assamese', 'active': False },
  { 'code': 'av', 'display_name': 'Avaric', 'active': False },
  { 'code': 'ae', 'display_name': 'Avestan', 'active': False },
  { 'code': 'ay', 'display_name': 'Aymara', 'active': False },
  { 'code': 'az', 'display_name': 'Azerbaijani', 'active': False },
  { 'code': 'bm', 'display_name': 'Bambara', 'active': False },
  { 'code': 'ba', 'display_name': 'Bashkir', 'active': False },
  { 'code': 'eu', 'display_name': 'Basque', 'active': True },
  { 'code': 'be', 'display_name': 'Belarusian', 'active': False },
  { 'code': 'bn', 'display_name': 'Bengali', 'active': True },
  { 'code': 'bh', 'display_name': 'Bihari', 'active': False },
  { 'code': 'bi', 'display_name': 'Bislama', 'active': False },
  { 'code': 'bs', 'display_name': 'Bosnian', 'active': False },
  { 'code': 'br', 'display_name': 'Breton', 'active': False },
  { 'code': 'bg', 'display_name': 'Bulgarian', 'active': True },
  { 'code': 'my', 'display_name': 'Burmese', 'active': False },
  { 'code': 'ca', 'display_name': 'Catalan', 'active': True },
  { 'code': 'ch', 'display_name': 'Chamorro', 'active': False },
  { 'code': 'ce', 'display_name': 'Chechen', 'active': False },
  { 'code': 'ny', 'display_name': 'Chichewa; Chewa; Nyanja', 'active': False },
  { 'code': 'zh', 'display_name': 'Chinese', 'active': False },
  { 'code': 'cv', 'display_name': 'Chuvash', 'active': False },
  { 'code': 'kw', 'display_name': 'Cornish', 'active': False },
  { 'code': 'co', 'display_name': 'Corsican', 'active': False },
  { 'code': 'cr', 'display_name': 'Cree', 'active': False },
  { 'code': 'hr', 'display_name': 'Croatian', 'active': True },
  { 'code': 'cs', 'display_name': 'Czech', 'active': True },
  { 'code': 'da', 'display_name': 'Danish', 'active': True },
  { 'code': 'dv', 'display_name': 'Divehi; Maldivian;', 'active': False },
  { 'code': 'nl', 'display_name': 'Dutch', 'active': True },
  { 'code': 'dz', 'display_name': 'Dzongkha', 'active': False },
  { 'code': 'en', 'display_name': 'English', 'active': True },
  { 'code': 'eo', 'display_name': 'Esperanto', 'active': False },
  { 'code': 'et', 'display_name': 'Estonian', 'active': True },
  { 'code': 'ee', 'display_name': 'Ewe', 'active': False },
  { 'code': 'fo', 'display_name': 'Faroese', 'active': False },
  { 'code': 'fj', 'display_name': 'Fijian', 'active': False },
  { 'code': 'fi', 'display_name': 'Finnish', 'active': True },
  { 'code': 'fr', 'display_name': 'French', 'active': True },
  { 'code': 'ff', 'display_name': 'Fula', 'active': False },
  { 'code': 'gl', 'display_name': 'Galician', 'active': False },
  { 'code': 'ka', 'display_name': 'Georgian', 'active': False },
  { 'code': 'de', 'display_name': 'German', 'active': True },
  { 'code': 'el', 'display_name': 'Greek', 'active': True },
  { 'code': 'gn', 'display_name': 'Guaraní', 'active': False },
  { 'code': 'gu', 'display_name': 'Gujarati', 'active': True },
  { 'code': 'ht', 'display_name': 'Haitian', 'active': False },
  { 'code': 'ha', 'display_name': 'Hausa', 'active': False },
  { 'code': 'he', 'display_name': 'Hebrew', 'active': True },
  { 'code': 'hz', 'display_name': 'Herero', 'active': False },
  { 'code': 'hi', 'display_name': 'Hindi', 'active': True },
  { 'code': 'ho', 'display_name': 'Hiri Motu', 'active': False },
  { 'code': 'hu', 'display_name': 'Hungarian', 'active': True },
  { 'code': 'ia', 'display_name': 'Interlingua', 'active': False },
  { 'code': 'id', 'display_name': 'Indonesian', 'active': True },
  { 'code': 'ie', 'display_name': 'Interlingue', 'active': False },
  { 'code': 'ga', 'display_name': 'Irish', 'active': False },
  { 'code': 'ig', 'display_name': 'Igbo', 'active': False },
  { 'code': 'ik', 'display_name': 'Inupiaq', 'active': False },
  { 'code': 'io', 'display_name': 'Ido', 'active': False },
  { 'code': 'is', 'display_name': 'Icelandic', 'active': True },
  { 'code': 'it', 'display_name': 'Italian', 'active': True },
  { 'code': 'iu', 'display_name': 'Inuktitut', 'active': False },
  { 'code': 'ja', 'display_name': 'Japanese', 'active': True },
  { 'code': 'jv', 'display_name': 'Javanese', 'active': False },
  { 'code': 'kl', 'display_name': 'Kalaallisut', 'active': False },
  { 'code': 'kn', 'display_name': 'Kannada', 'active': True },
  { 'code': 'kr', 'display_name': 'Kanuri', 'active': False },
  { 'code': 'ks', 'display_name': 'Kashmiri', 'active': False },
  { 'code': 'kk', 'display_name': 'Kazakh', 'active': False },
  { 'code': 'km', 'display_name': 'Khmer', 'active': False },
  { 'code': 'ki', 'display_name': 'Kikuyu, Gikuyu', 'active': False },
  { 'code': 'rw', 'display_name': 'Kinyarwanda', 'active': False },
  { 'code': 'ky', 'display_name': 'Kirghiz, Kyrgyz', 'active': False },
  { 'code': 'kv', 'display_name': 'Komi', 'active': False },
  { 'code': 'kg', 'display_name': 'Kongo', 'active': False },
  { 'code': 'ko', 'display_name': 'Korean', 'active': True },
  { 'code': 'ku', 'display_name': 'Kurdish', 'active': False },
  { 'code': 'kj', 'display_name': 'Kwanyama, Kuanyama', 'active': False },
  { 'code': 'la', 'display_name': 'Latin', 'active': False },
  { 'code': 'lb', 'display_name': 'Luxembourgish', 'active': False },
  { 'code': 'lg', 'display_name': 'Luganda', 'active': False },
  { 'code': 'li', 'display_name': 'Limburgish', 'active': False },
  { 'code': 'ln', 'display_name': 'Lingala', 'active': False },
  { 'code': 'lo', 'display_name': 'Lao', 'active': False },
  { 'code': 'lt', 'display_name': 'Lithuanian', 'active': True },
  { 'code': 'lu', 'display_name': 'Luba-Katanga', 'active': False },
  { 'code': 'lv', 'display_name': 'Latvian', 'active': True },
  { 'code': 'gv', 'display_name': 'Manx', 'active': False },
  { 'code': 'mk', 'display_name': 'Macedonian', 'active': False },
  { 'code': 'mg', 'display_name': 'Malagasy', 'active': False },
  { 'code': 'ms', 'display_name': 'Malay', 'active': True },
  { 'code': 'ml', 'display_name': 'Malayalam', 'active': True },
  { 'code': 'mt', 'display_name': 'Maltese', 'active': False },
  { 'code': 'mi', 'display_name': 'Māori', 'active': False },
  { 'code': 'mr', 'display_name': 'Marathi', 'active': True },
  { 'code': 'mh', 'display_name': 'Marshallese', 'active': False },
  { 'code': 'mn', 'display_name': 'Mongolian', 'active': False },
  { 'code': 'na', 'display_name': 'Nauru', 'active': False },
  { 'code': 'nv', 'display_name': 'Navajo, Navaho', 'active': False },
  { 'code': 'nb', 'display_name': 'Norwegian Bokmål', 'active': False },
  { 'code': 'nd', 'display_name': 'North Ndebele', 'active': False },
  { 'code': 'ne', 'display_name': 'Nepali', 'active': False },
  { 'code': 'ng', 'display_name': 'Ndonga', 'active': False },
  { 'code': 'nn', 'display_name': 'Norwegian Nynorsk', 'active': False },
  { 'code': 'no', 'display_name': 'Norwegian', 'active': True },
  { 'code': 'ii', 'display_name': 'Nuosu', 'active': False },
  { 'code': 'nr', 'display_name': 'South Ndebele', 'active': False },
  { 'code': 'oc', 'display_name': 'Occitan', 'active': False },
  { 'code': 'oj', 'display_name': 'Ojibwe, Ojibwa', 'active': False },
  { 'code': 'cu', 'display_name': 'Old Church Slavonic', 'active': False },
  { 'code': 'om', 'display_name': 'Oromo', 'active': False },
  { 'code': 'or', 'display_name': 'Oriya', 'active': False },
  { 'code': 'os', 'display_name': 'Ossetian, Ossetic', 'active': False },
  { 'code': 'pa', 'display_name': 'Panjabi, Punjabi', 'active': False },
  { 'code': 'pi', 'display_name': 'Pāli', 'active': False },
  { 'code': 'fa', 'display_name': 'Persian', 'active': False },
  { 'code': 'pl', 'display_name': 'Polish', 'active': True },
  { 'code': 'ps', 'display_name': 'Pashto, Pushto', 'active': False },
  { 'code': 'pt', 'display_name': 'Portuguese', 'active': True },
  { 'code': 'qu', 'display_name': 'Quechua', 'active': False },
  { 'code': 'rm', 'display_name': 'Romansh', 'active': False },
  { 'code': 'rn', 'display_name': 'Kirundi', 'active': False },
  { 'code': 'ro', 'display_name': 'Romanian', 'active': True },
  { 'code': 'ru', 'display_name': 'Russian', 'active': True },
  { 'code': 'sa', 'display_name': 'Sanskrit(Saṁskṛta)', 'active': False },
  { 'code': 'sc', 'display_name': 'Sardinian', 'active': False },
  { 'code': 'sd', 'display_name': 'Sindhi', 'active': False },
  { 'code': 'se', 'display_name': 'Northern Sami', 'active': False },
  { 'code': 'sm', 'display_name': 'Samoan', 'active': False },
  { 'code': 'sg', 'display_name': 'Sango', 'active': False },
  { 'code': 'sr', 'display_name': 'Serbian', 'active': True },
  { 'code': 'gd', 'display_name': 'Scottish Gaelic', 'active': False },
  { 'code': 'sn', 'display_name': 'Shona', 'active': False },
  { 'code': 'si', 'display_name': 'Sinhala, Sinhalese', 'active': False },
  { 'code': 'sk', 'display_name': 'Slovak', 'active': True },
  { 'code': 'sl', 'display_name': 'Slovenian', 'active': True },
  { 'code': 'so', 'display_name': 'Somali', 'active': False },
  { 'code': 'st', 'display_name': 'Southern Sotho', 'active': False },
  { 'code': 'es', 'display_name': 'Spanish', 'active': True },
  { 'code': 'su', 'display_name': 'Sundanese', 'active': False },
  { 'code': 'sw', 'display_name': 'Swahili', 'active': True },
  { 'code': 'ss', 'display_name': 'Swati', 'active': False },
  { 'code': 'sv', 'display_name': 'Swedish', 'active': True },
  { 'code': 'ta', 'display_name': 'Tamil', 'active': True },
  { 'code': 'te', 'display_name': 'Telugu', 'active': True },
  { 'code': 'tg', 'display_name': 'Tajik', 'active': False },
  { 'code': 'th', 'display_name': 'Thai', 'active': True },
  { 'code': 'ti', 'display_name': 'Tigrinya', 'active': False },
  { 'code': 'bo', 'display_name': 'Tibetan', 'active': False },
  { 'code': 'tk', 'display_name': 'Turkmen', 'active': False },
  { 'code': 'tl', 'display_name': 'Tagalog', 'active': False },
  { 'code': 'tn', 'display_name': 'Tswana', 'active': False },
  { 'code': 'to', 'display_name': 'Tonga', 'active': False },
  { 'code': 'tr', 'display_name': 'Turkish', 'active': True },
  { 'code': 'ts', 'display_name': 'Tsonga', 'active': False },
  { 'code': 'tt', 'display_name': 'Tatar', 'active': False },
  { 'code': 'tw', 'display_name': 'Twi', 'active': False },
  { 'code': 'ty', 'display_name': 'Tahitian', 'active': False },
  { 'code': 'ug', 'display_name': 'Uighur, Uyghur', 'active': False },
  { 'code': 'uk', 'display_name': 'Ukrainian', 'active': True },
  { 'code': 'ur', 'display_name': 'Urdu', 'active': True },
  { 'code': 'uz', 'display_name': 'Uzbek', 'active': False },
  { 'code': 've', 'display_name': 'Venda', 'active': False },
  { 'code': 'vi', 'display_name': 'Vietnamese', 'active': True },
  { 'code': 'vo', 'display_name': 'Volapük', 'active': False },
  { 'code': 'wa', 'display_name': 'Walloon', 'active': False },
  { 'code': 'cy', 'display_name': 'Welsh', 'active': True },
  { 'code': 'wo', 'display_name': 'Wolof', 'active': False },
  { 'code': 'fy', 'display_name': 'Western Frisian', 'active': False },
  { 'code': 'xh', 'display_name': 'Xhosa', 'active': False },
  { 'code': 'yi', 'display_name': 'Yiddish', 'active': False },
  { 'code': 'yo', 'display_name': 'Yoruba', 'active': False },
  { 'code': 'za', 'display_name': 'Zhuang, Chuang', 'active': False },
  { 'code': 'zu', 'display_name': 'Zulu', 'active': False },
)

DEFAULT_LANGUAGE_CODE = 'en'

APP_LANGUAGE_CODES = tuple(
  lang['code'] for lang in BCP_47_LANGUAGES if lang.get('active', False)
)

APP_LANGUAGES = tuple(
  sorted(
    (lang for lang in BCP_47_LANGUAGES if lang.get('active', False)),
    key=lambda lang: lang['display_name']
  )
)

APP_LANGUAGE_CODE_CHOICES = tuple((code, code) for code in APP_LANGUAGE_CODES)
