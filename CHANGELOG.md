# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [v2.5.1](https://github.com/tj-django/django-clone/releases/tag/v2.5.1) - 2021-04-22

<small>[Compare with v2.5.0](https://github.com/tj-django/django-clone/compare/v2.5.0...v2.5.1)</small>

### Added
- Added .editorconfig ([e8dc042](https://github.com/tj-django/django-clone/commit/e8dc042718de23edcff9b04aaa7737c740a63db3) by Tonye Jack).


## [v2.5.0](https://github.com/tj-django/django-clone/releases/tag/v2.5.0) - 2021-04-21

<small>[Compare with v2.4.0](https://github.com/tj-django/django-clone/compare/v2.4.0...v2.5.0)</small>

### Added
- Added black pre-commit hook (#284) ([7d4a36b](https://github.com/tj-django/django-clone/commit/7d4a36be428b8431644b4f873ca51fe2011c5ddf) by Tonye Jack).

### Fixed
- Fix bugs for related_name and m2o clone (#281) ([53eb444](https://github.com/tj-django/django-clone/commit/53eb444e7e939f6c123c2b00ff0761c740955116) by Yuekui).


## [v2.4.0](https://github.com/tj-django/django-clone/releases/tag/v2.4.0) - 2021-04-16

<small>[Compare with v2.3.3](https://github.com/tj-django/django-clone/compare/v2.3.3...v2.4.0)</small>

### Added
- Add a delay to resolve inconsistency in windows (#266) ([59ab32d](https://github.com/tj-django/django-clone/commit/59ab32d318c1478da14965fe6dec8986dbe5ba55) by Tonye Jack).


## [v2.3.3](https://github.com/tj-django/django-clone/releases/tag/v2.3.3) - 2021-04-09

<small>[Compare with v2.3.2](https://github.com/tj-django/django-clone/compare/v2.3.2...v2.3.3)</small>


## [v2.3.2](https://github.com/tj-django/django-clone/releases/tag/v2.3.2) - 2021-04-08

<small>[Compare with v2.3.1](https://github.com/tj-django/django-clone/compare/v2.3.1...v2.3.2)</small>

### Fixed
- Fixed test. ([0945265](https://github.com/tj-django/django-clone/commit/0945265bf3860dbb7c9a151066b3fe1a58f52d6d) by Tonye Jack).
- Fixed formatting. ([9ae328b](https://github.com/tj-django/django-clone/commit/9ae328be5b7c3a6f6f2a5bf2827aab96aee6178d) by Tonye Jack).


## [v2.3.1](https://github.com/tj-django/django-clone/releases/tag/v2.3.1) - 2021-04-08

<small>[Compare with v2.3.0](https://github.com/tj-django/django-clone/compare/v2.3.0...v2.3.1)</small>

### Added
- Added .github/workflows/release.yml ([d739de6](https://github.com/tj-django/django-clone/commit/d739de6ca214e95d1cf98e9ba89103a90501c49b) by Tonye Jack).


## [v2.3.0](https://github.com/tj-django/django-clone/releases/tag/v2.3.0) - 2021-04-08

<small>[Compare with v2.2.1](https://github.com/tj-django/django-clone/compare/v2.2.1...v2.3.0)</small>

### Fixed
- Fix bug with o2o fields (#255) ([cdd3d0a](https://github.com/tj-django/django-clone/commit/cdd3d0a0ceee3a6ed098a8319f190eae02ea6633) by Tonye Jack).
- Fixed bug with cloning o2o fields (#252) ([342eca8](https://github.com/tj-django/django-clone/commit/342eca8a2bfad5b90432c733c7ff777cef8f50bd) by Tonye Jack).
- Fix code style issues with black ([197d0a4](https://github.com/tj-django/django-clone/commit/197d0a4b9ecd62c5032b8aad4a2990e8c6ff18a2) by Lint Action).


## [v2.2.1](https://github.com/tj-django/django-clone/releases/tag/v2.2.1) - 2021-04-07

<small>[Compare with v2.2.0](https://github.com/tj-django/django-clone/compare/v2.2.0...v2.2.1)</small>

### Fixed
- Fixed typo with filename. ([30b9a92](https://github.com/tj-django/django-clone/commit/30b9a928206f918dfb2bea1c6cb7b102ac61fd86) by Tonye Jack).


## [v2.2.0](https://github.com/tj-django/django-clone/releases/tag/v2.2.0) - 2021-04-07

<small>[Compare with v2.1.1](https://github.com/tj-django/django-clone/compare/v2.1.1...v2.2.0)</small>

### Added
- Added migration. ([c938488](https://github.com/tj-django/django-clone/commit/c938488abc8e8a7476e0da86a3db1128b15255d9) by Tonye Jack).
- Added .github/workflows/sync-release-version.yml ([6bdce7c](https://github.com/tj-django/django-clone/commit/6bdce7cc5a834040a84441880231c71a576f5e86) by Tonye Jack).
- Added .github/auto-approve.yml ([47538b5](https://github.com/tj-django/django-clone/commit/47538b54bdd89b277539451c346a26ed57608323) by Tonye Jack).
- Added .github/workflows/auto-approve.yml ([8f4bba0](https://github.com/tj-django/django-clone/commit/8f4bba0ee8b50008544baa204719b461ce2d823b) by Tonye Jack).

### Fixed
- Fix code style issues with black ([b295af9](https://github.com/tj-django/django-clone/commit/b295af98c5208a45dba0680604d7ccf8b5e0649a) by Lint Action).
- Fixed bug using pre_save. ([bc1ec5f](https://github.com/tj-django/django-clone/commit/bc1ec5f98b468cf8adac4956218f4d36ccde04e2) by Tonye Jack).
- Fixed saving date/datetime fields. ([13b5959](https://github.com/tj-django/django-clone/commit/13b5959e4f89e6e0e46fe284f693ed1aff7022ca) by Tonye Jack).

### Removed
- Remove whitespace. ([e60b52a](https://github.com/tj-django/django-clone/commit/e60b52a5ebc4eb7e0040092e8f62b35989b1c6ca) by Tonye Jack).


## [v2.1.1](https://github.com/tj-django/django-clone/releases/tag/v2.1.1) - 2021-03-25

<small>[Compare with v2.1.0](https://github.com/tj-django/django-clone/compare/v2.1.0...v2.1.1)</small>


## [v2.1.0](https://github.com/tj-django/django-clone/releases/tag/v2.1.0) - 2021-03-25

<small>[Compare with v2.0.2](https://github.com/tj-django/django-clone/compare/v2.0.2...v2.1.0)</small>

### Fixed
- Fix code style issues with black ([08f6a3c](https://github.com/tj-django/django-clone/commit/08f6a3c8e3e733392eabec6693ad6b3a6969394f) by Lint Action).
- Fixed lint errors. ([8286951](https://github.com/tj-django/django-clone/commit/82869511299afbca5e44bd79bafb9b9b154d05f7) by Tonye Jack).


## [v2.0.2](https://github.com/tj-django/django-clone/releases/tag/v2.0.2) - 2021-03-24

<small>[Compare with v2.0.1](https://github.com/tj-django/django-clone/compare/v2.0.1...v2.0.2)</small>

### Fixed
- Fix code style issues with black ([1a450ef](https://github.com/tj-django/django-clone/commit/1a450ef545aa04d17de1db74720d4e110e476a98) by Lint Action).
- Fixed test ([34a77e6](https://github.com/tj-django/django-clone/commit/34a77e68133c1f417947f408818decafd074ada6) by Tonye Jack).
- Fixed lint errors. ([5f4b4ea](https://github.com/tj-django/django-clone/commit/5f4b4eae1c313565cad43efea6d38c2c41e8671b) by Tonye Jack).
- Fixed bug with cloning slugs. ([bdb6029](https://github.com/tj-django/django-clone/commit/bdb60295f84359ed9f43fea31af2f0c076c5d623) by Tonye Jack).
- Fixed short description. ([64ce104](https://github.com/tj-django/django-clone/commit/64ce104f03c5718a1e5b95e256b5d50700ff8803) by Tonye Jack).
- Fixed migrations. ([4ede994](https://github.com/tj-django/django-clone/commit/4ede9947c2a6528598766a7b3cec04fb105d03b6) by Tonye Jack).
- Fixed type hints. ([afae2d7](https://github.com/tj-django/django-clone/commit/afae2d7f9dd46f3394015a142f9a85d4d45e0ea8) by Tonye Jack).
- Fixed clean. ([3ead462](https://github.com/tj-django/django-clone/commit/3ead462bc16c79594609539de73aa89a51019f5a) by Tonye Jack).
- Fixed imports. ([5e04253](https://github.com/tj-django/django-clone/commit/5e042538055ed9860cd2bd9d78cd7683dc4cd376) by Tonye Jack).


## [v2.0.1](https://github.com/tj-django/django-clone/releases/tag/v2.0.1) - 2021-03-24

<small>[Compare with v2.0.0](https://github.com/tj-django/django-clone/compare/v2.0.0...v2.0.1)</small>

### Fixed
- Fix code style issues with black ([408303a](https://github.com/tj-django/django-clone/commit/408303a2b2ce38d0cb8b76e5b5beac7030c90d30) by Lint Action).
- Fixed typo. ([d20c3d5](https://github.com/tj-django/django-clone/commit/d20c3d51d8ac4d1830b0006108d8cd2e614b9e43) by Tonye Jack).

### Removed
- Remove old name ([f82dab7](https://github.com/tj-django/django-clone/commit/f82dab7b1585288c68e188b5c79bccf0551ae5fe) by Tonye Jack).


## [v2.0.0](https://github.com/tj-django/django-clone/releases/tag/v2.0.0) - 2021-03-20

<small>[Compare with v1.1.10](https://github.com/tj-django/django-clone/compare/v1.1.10...v2.0.0)</small>

### Added
- Added spacing. ([af86ae6](https://github.com/tj-django/django-clone/commit/af86ae6b570cb2c1101d59814e7dadb3b897eb9e) by Tonye Jack).
- Added docs. ([a35d976](https://github.com/tj-django/django-clone/commit/a35d976f0fdeead88736bd9c2395434ed5aa2c3a) by Tonye Jack).

### Fixed
- Fix code style issues with black ([fb1377f](https://github.com/tj-django/django-clone/commit/fb1377f704b1bce4f69286e484eac0b6515b6f63) by Lint Action).
- Fixed lint errors. ([43f9887](https://github.com/tj-django/django-clone/commit/43f9887e61c13607bdd80212f0c37fd1919671f4) by Tonye Jack).
- Fixed token. ([237b2f1](https://github.com/tj-django/django-clone/commit/237b2f173cc69a80125f1c67712d82d43b17ff19) by Tonye Jack).

### Removed
- Removed unused code ([18943b6](https://github.com/tj-django/django-clone/commit/18943b69227340e7dddc2e1416c058db48d5b34f) by Tonye Jack).
- Remove parallel ([8929f85](https://github.com/tj-django/django-clone/commit/8929f855f7e77ae8ff7223ec5d4f0adf21db0b47) by Tonye Jack).


## [v1.1.10](https://github.com/tj-django/django-clone/releases/tag/v1.1.10) - 2020-12-05

<small>[Compare with v1.1.9](https://github.com/tj-django/django-clone/compare/v1.1.9...v1.1.10)</small>

### Fixed
- Fix code style issues with black ([49d8378](https://github.com/tj-django/django-clone/commit/49d837822689766f40c2ee0c0449f8a94907604b) by Lint Action).


## [v1.1.9](https://github.com/tj-django/django-clone/releases/tag/v1.1.9) - 2020-11-29

<small>[Compare with v1.1.8](https://github.com/tj-django/django-clone/compare/v1.1.8...v1.1.9)</small>

### Fixed
- Fixed lint errors. ([c93a953](https://github.com/tj-django/django-clone/commit/c93a953001137b73b555c6df9bc652f7ad2f2169) by Tonye Jack).


## [v1.1.8](https://github.com/tj-django/django-clone/releases/tag/v1.1.8) - 2020-11-07

<small>[Compare with v1.1.6](https://github.com/tj-django/django-clone/compare/v1.1.6...v1.1.8)</small>

### Added
- Add support for running workflow on forks ([a40a22e](https://github.com/tj-django/django-clone/commit/a40a22e0966916537109bbd4262edffe64052c73) by Tonye Jack).
- Add support for related manytomany fields ([0c88207](https://github.com/tj-django/django-clone/commit/0c88207cbb858c844bbee48f702cefa61e09403e) by Yuekui Li).

### Changed
- Change lint action back to v1 ([c53774c](https://github.com/tj-django/django-clone/commit/c53774c73a55a795a2c73ef2e5844c003b087b08) by Yuekui).

### Fixed
- Fixed lint errors. ([b01bb07](https://github.com/tj-django/django-clone/commit/b01bb07aab96238330dd4b133991aa14b1b68d1b) by Tonye Jack).
- Fix code style issues with black ([400e8f2](https://github.com/tj-django/django-clone/commit/400e8f213d87ad0a648a1412ad1b8d06d64944eb) by Lint Action).
- Fix typo ([29757bc](https://github.com/tj-django/django-clone/commit/29757bc9de045b20dac2751260c9dd4b6e90d1c4) by Yuekui).

### Removed
- Removed unused code. ([1a2308f](https://github.com/tj-django/django-clone/commit/1a2308feb527478842d4439d8f42cd57ebf42771) by Tonye Jack).


## [v1.1.6](https://github.com/tj-django/django-clone/releases/tag/v1.1.6) - 2020-09-07

<small>[Compare with v1.1.5](https://github.com/tj-django/django-clone/compare/v1.1.5...v1.1.6)</small>


## [v1.1.5](https://github.com/tj-django/django-clone/releases/tag/v1.1.5) - 2020-09-07

<small>[Compare with v1.1.4](https://github.com/tj-django/django-clone/compare/v1.1.4...v1.1.5)</small>

### Fixed
- Fixed issues with sdist. ([ca59c86](https://github.com/tj-django/django-clone/commit/ca59c866ce2fb09822c3a6aa723bf1bf2dc18d9a) by Tonye Jack).


## [v1.1.4](https://github.com/tj-django/django-clone/releases/tag/v1.1.4) - 2020-09-07

<small>[Compare with v1.1.3](https://github.com/tj-django/django-clone/compare/v1.1.3...v1.1.4)</small>


## [v1.1.3](https://github.com/tj-django/django-clone/releases/tag/v1.1.3) - 2020-09-07

<small>[Compare with v1.1.2](https://github.com/tj-django/django-clone/compare/v1.1.2...v1.1.3)</small>

### Fixed
- Fixed manifest.in ([df2e40b](https://github.com/tj-django/django-clone/commit/df2e40b137cab9c8968d738fa2428e06bc5dbf44) by Tonye Jack).


## [v1.1.2](https://github.com/tj-django/django-clone/releases/tag/v1.1.2) - 2020-09-07

<small>[Compare with v1.1.1](https://github.com/tj-django/django-clone/compare/v1.1.1...v1.1.2)</small>

### Added
- Added missing changes. ([37de0a6](https://github.com/tj-django/django-clone/commit/37de0a6824933d1891f4b97d563ba9e17064690f) by Tonye Jack).


## [v1.1.1](https://github.com/tj-django/django-clone/releases/tag/v1.1.1) - 2020-09-07

<small>[Compare with v1.1.0](https://github.com/tj-django/django-clone/compare/v1.1.0...v1.1.1)</small>

### Added
- Added missing changes. ([64ec246](https://github.com/tj-django/django-clone/commit/64ec24661615d8d143081d2ad43ad4d9c97b1e1a) by Tonye Jack).

### Fixed
- Fixed makefile. ([9815226](https://github.com/tj-django/django-clone/commit/9815226ab63c363dfc09e450b93b917ced9828ff) by Tonye Jack).


## [v1.1.0](https://github.com/tj-django/django-clone/releases/tag/v1.1.0) - 2020-09-07

<small>[Compare with v1.0.0](https://github.com/tj-django/django-clone/compare/v1.0.0...v1.1.0)</small>


## [v1.0.0](https://github.com/tj-django/django-clone/releases/tag/v1.0.0) - 2020-09-05

<small>[Compare with v0.2.0](https://github.com/tj-django/django-clone/compare/v0.2.0...v1.0.0)</small>

### Added
- Add migrations ([1d9c68e](https://github.com/tj-django/django-clone/commit/1d9c68e84793f02415139ae7bac1f0c18da82a71) by Yuekui Li).

### Fixed
- Fix code style issues with black ([6249abe](https://github.com/tj-django/django-clone/commit/6249abe494cec23448d6fff09b7aa0eb2cf7978a) by Lint Action).
- Fixed test. ([240cc7c](https://github.com/tj-django/django-clone/commit/240cc7cb171d2d89c500e34c0511ab15a25d71f3) by Tonye Jack).
- Fixed github action. ([80bdd3e](https://github.com/tj-django/django-clone/commit/80bdd3ec6221b683957f4abf321130e599be174e) by Tonye Jack).
- Fixed flake8 error. ([7845ede](https://github.com/tj-django/django-clone/commit/7845ede0cbbf4a0d762f481dd184939096f8be17) by Tonye Jack).
- Fix invalid enum field value for unique_together fields ([1f83bf8](https://github.com/tj-django/django-clone/commit/1f83bf8472b47739c3a879a9b40199630178336a) by Yuekui Li).


## [v0.2.0](https://github.com/tj-django/django-clone/releases/tag/v0.2.0) - 2020-06-04

<small>[Compare with v0.1.6](https://github.com/tj-django/django-clone/compare/v0.1.6...v0.2.0)</small>

### Removed
- Removed unused code. ([6f3f515](https://github.com/tj-django/django-clone/commit/6f3f5158d8b21ab24d8743cc4b33823aa347aa44) by Tonye Jack).


## [v0.1.6](https://github.com/tj-django/django-clone/releases/tag/v0.1.6) - 2020-06-04

<small>[Compare with v0.1.5](https://github.com/tj-django/django-clone/compare/v0.1.5...v0.1.6)</small>

### Added
- Add renovate.json ([99d54b5](https://github.com/tj-django/django-clone/commit/99d54b5e5ff9eb3a759edf0d3610f1d587f69429) by Renovate Bot).

### Fixed
- Fixed unused imports. ([14e40e2](https://github.com/tj-django/django-clone/commit/14e40e2d42a9f016a9520f88e52f03ac40cd8768) by Tonye Jack).
- Fixed bug with index. ([dcd6256](https://github.com/tj-django/django-clone/commit/dcd625685b3b921d09526901a7458ac56389dda1) by Tonye Jack).
- Fixed lint errors. ([888d88d](https://github.com/tj-django/django-clone/commit/888d88d5605fb8ba7ebf19fd91d4cd1eca318e13) by Tonye Jack).
- Fixed test. ([ac7af5f](https://github.com/tj-django/django-clone/commit/ac7af5f973a54f2f4c59df403edf26dc38d51bd5) by Tonye Jack).

### Removed
- Remove the information for updating installed_apps ([4a4aa8c](https://github.com/tj-django/django-clone/commit/4a4aa8c0ef3a6943b8cfe43fae96c522d6126111) by Tonye Jack).


## [v0.1.5](https://github.com/tj-django/django-clone/releases/tag/v0.1.5) - 2020-05-12

<small>[Compare with v0.1.4](https://github.com/tj-django/django-clone/compare/v0.1.4...v0.1.5)</small>


## [v0.1.4](https://github.com/tj-django/django-clone/releases/tag/v0.1.4) - 2020-05-12

<small>[Compare with v0.1.3](https://github.com/tj-django/django-clone/compare/v0.1.3...v0.1.4)</small>

### Fixed
- Fixed typo. ([1613037](https://github.com/tj-django/django-clone/commit/16130379a65be64a5cc87ba716d300a3ac34a196) by Tonye Jack).
- Fixed formatting ([db2bfb2](https://github.com/tj-django/django-clone/commit/db2bfb27196b6187f2e07e3db85ac3129c70615f) by Tonye Jack).
- Fixed test errors ([f773001](https://github.com/tj-django/django-clone/commit/f773001fc8dc0f3811f74bd630b8c8e54e622992) by Tonye Jack).
- Fixed lint errors ([1a0900a](https://github.com/tj-django/django-clone/commit/1a0900ada94751908d671405c1c89e9c316926c8) by Tonye Jack).
- Fixed version. ([969b562](https://github.com/tj-django/django-clone/commit/969b562276ec908961c84296043ec9ba65a7f86e) by Tonye Jack).
- Fixed test. ([f66e745](https://github.com/tj-django/django-clone/commit/f66e74556c8924189f417a6195272b7267d92afb) by Tonye Jack).
- Fixed ordering. ([07d5f64](https://github.com/tj-django/django-clone/commit/07d5f64eb65fcf6962c238ebb26a2580770f4aa0) by Tonye Jack).

### Removed
- Remove unused line. ([7d6339a](https://github.com/tj-django/django-clone/commit/7d6339a8eba8e8d661b3004274a9fdfccf7afd55) by Tonye Jack).


## [v0.1.3](https://github.com/tj-django/django-clone/releases/tag/v0.1.3) - 2020-04-16

<small>[Compare with v0.1.2](https://github.com/tj-django/django-clone/compare/v0.1.2...v0.1.3)</small>

### Fixed
- Fixed typo ([e2f9643](https://github.com/tj-django/django-clone/commit/e2f9643ffd165adbe98c343293936b879061056d) by Tonye Jack).
- Fixed example documentation. ([b6ceae9](https://github.com/tj-django/django-clone/commit/b6ceae92bae52e7efa49789ffcd1cb7b749a8546) by Tonye Jack).
- Fixed lint errors. ([a72040d](https://github.com/tj-django/django-clone/commit/a72040d601a19e341d39381510c949d2f2316251) by Tonye Jack).
- Fix lint errors ([9dab0f7](https://github.com/tj-django/django-clone/commit/9dab0f7c5d7c6105d1552d3130050aa0889f94df) by Tonye Jack).
- Fixed invalid config. ([d33354b](https://github.com/tj-django/django-clone/commit/d33354ba8f83c5c694f52512db0575ce12d6fa19) by Tonye Jack).

### Removed
- Removed trailing whitespace. ([6933020](https://github.com/tj-django/django-clone/commit/6933020271094b054a9753e64a75d1064bb2fdb7) by Tonye Jack).
- Removed unused line ([0307889](https://github.com/tj-django/django-clone/commit/0307889c5550b098fa8cf553c91d0a5b3756b1ff) by Tonye Jack).


## [v0.1.2](https://github.com/tj-django/django-clone/releases/tag/v0.1.2) - 2019-12-03

<small>[Compare with v0.1.1](https://github.com/tj-django/django-clone/compare/v0.1.1...v0.1.2)</small>

### Fixed
- Fixed test. ([5b65a84](https://github.com/tj-django/django-clone/commit/5b65a842380d30ec84e4e6d3db882702385bfec8) by Tonye Jack).
- Fixed flake8 errors. ([ac0c27b](https://github.com/tj-django/django-clone/commit/ac0c27b2a93c10c29b3a32990752d3c544bf9619) by Tonye Jack).

### Removed
- Removed unused line. ([4e1d5d1](https://github.com/tj-django/django-clone/commit/4e1d5d144acccfb8a15a8551ce3902338387467b) by Tonye Jack).
- Remove tabs. ([f8c1a46](https://github.com/tj-django/django-clone/commit/f8c1a46e77c5c1ec42f4fc84af6872d2861a8a69) by Tonye Jack).
- Remove unused code. ([ecfa4b6](https://github.com/tj-django/django-clone/commit/ecfa4b623ed4456cff431095f4b62ec41badb829) by Tonye Jack).


## [v0.1.1](https://github.com/tj-django/django-clone/releases/tag/v0.1.1) - 2019-12-02

<small>[Compare with v0.1.0](https://github.com/tj-django/django-clone/compare/v0.1.0...v0.1.1)</small>

### Added
- Added pypi badge. ([e0a09e4](https://github.com/tj-django/django-clone/commit/e0a09e4dd084fd7ffe2c95a66aaa1a5b09762d78) by Tonye Jack).
- Added spec for cloning in parallel. ([bede5de](https://github.com/tj-django/django-clone/commit/bede5de00cd40a610c65d9d8ae19fa270cf8fc41) by Tonye Jack).

### Fixed
- Fixed indentation. ([75214a5](https://github.com/tj-django/django-clone/commit/75214a5b786a5322b8aa2af59fc95f6d0d10a78c) by Tonye Jack).
- Fixed flake8 error. ([b28fb8c](https://github.com/tj-django/django-clone/commit/b28fb8c5f67f1ef9b790fa7f0ac3e9b106544d6f) by Tonye Jack).
- Fixed example. ([1ad41d3](https://github.com/tj-django/django-clone/commit/1ad41d3f2866136a53d4fc0f91ded97ffe5f7f89) by Tonye Jack).
- Fixed test. ([ec39547](https://github.com/tj-django/django-clone/commit/ec395478f1ecfce4a1d1a0afbc8f0299d5f4c6dc) by Tonye Jack).
- Fixed lint errors and added support for running autopep8. ([4537a46](https://github.com/tj-django/django-clone/commit/4537a460de92d0ef34c875d37439f79c26a69d36) by Tonye Jack).
- Fix bug with cloning unique fields and added support for bulk_clone. ([70e76a8](https://github.com/tj-django/django-clone/commit/70e76a81e6497ef52a2d525bc4a5e6a27d5b0e75) by Tonye Jack).
- Fix typo clonemodeladmin -> clonemodeladmin ([b8a29c2](https://github.com/tj-django/django-clone/commit/b8a29c240aba7f7736ef297a69f54eb0a399d1ad) by SebastianKapunkt).

### Removed
- Remove .extend. ([3e31e86](https://github.com/tj-django/django-clone/commit/3e31e86ab49d834cc2aad89760fa2a25eff687df) by Tonye Jack).


## [v0.1.0](https://github.com/tj-django/django-clone/releases/tag/v0.1.0) - 2019-11-23

<small>[Compare with v0.0.11](https://github.com/tj-django/django-clone/compare/v0.0.11...v0.1.0)</small>


## [v0.0.11](https://github.com/tj-django/django-clone/releases/tag/v0.0.11) - 2019-11-23

<small>[Compare with v0.0.10](https://github.com/tj-django/django-clone/compare/v0.0.10...v0.0.11)</small>

### Fixed
- Fixed lint errors. ([5b9ceae](https://github.com/tj-django/django-clone/commit/5b9ceae369da2322ee6cdbed785b0fab74275aad) by Tonye Jack).
- Fixed indentation. ([18e382d](https://github.com/tj-django/django-clone/commit/18e382d9b23872a725c97ab44333e4a354d2c123) by Tonye Jack).
- Fixed duplicate context ([be24df3](https://github.com/tj-django/django-clone/commit/be24df310abd82f4c7d716b18da82c376246578f) by Tonye Jack).
- Fixed yaml lint errors. ([ec949cb](https://github.com/tj-django/django-clone/commit/ec949cb75bcab1783e417e19ea3c04efa86b9658) by Tonye Jack).
- Fixed flake8 errors. ([133d404](https://github.com/tj-django/django-clone/commit/133d404acf49bf134f382bd98e06395fde7abe1f) by Tonye Jack).

### Removed
- Removed unused file. ([bc869a7](https://github.com/tj-django/django-clone/commit/bc869a78428ef27f8af0f2abdb11e56331faa4c3) by Tonye Jack).
- Removed node_modules. ([ae75573](https://github.com/tj-django/django-clone/commit/ae75573519bc6223ccdbe905ed49f4c3f050da18) by Tonye Jack).
- Removed empty config ([b779051](https://github.com/tj-django/django-clone/commit/b77905110a26ba96d22967cdb761e552dd0d8c6a) by Tonye Jack).


## [v0.0.10](https://github.com/tj-django/django-clone/releases/tag/v0.0.10) - 2019-11-12

<small>[Compare with v0.0.9](https://github.com/tj-django/django-clone/compare/v0.0.9...v0.0.10)</small>

### Fixed
- Fixed manage.py. ([eaa73f6](https://github.com/tj-django/django-clone/commit/eaa73f6687b4bf586cd4c6468819a615aea76d37) by Tonye Jack).
- Fixed pyenv. ([66aabd5](https://github.com/tj-django/django-clone/commit/66aabd5536d6b924d56b4a04180c460fdc399449) by Tonye Jack).
- Fixed tox. ([82afdde](https://github.com/tj-django/django-clone/commit/82afdde7929d85b55bec6e4ad8784e268564bbee) by Tonye Jack).
- Fixed python27. ([20b3c55](https://github.com/tj-django/django-clone/commit/20b3c55ecaa376d8069134427b39ce857c218931) by Tonye Jack).

### Removed
- Removed bumpversion==0.5.3. ([60a18e5](https://github.com/tj-django/django-clone/commit/60a18e57e7e4b98335cc7c612c25e77f8a5b4564) by Tonye Jack).


## [v0.0.9](https://github.com/tj-django/django-clone/releases/tag/v0.0.9) - 2019-11-10

<small>[Compare with v0.0.8](https://github.com/tj-django/django-clone/compare/v0.0.8...v0.0.9)</small>


## [v0.0.8](https://github.com/tj-django/django-clone/releases/tag/v0.0.8) - 2019-11-10

<small>[Compare with v0.0.7](https://github.com/tj-django/django-clone/compare/v0.0.7...v0.0.8)</small>


## [v0.0.7](https://github.com/tj-django/django-clone/releases/tag/v0.0.7) - 2019-11-10

<small>[Compare with v0.0.6](https://github.com/tj-django/django-clone/compare/v0.0.6...v0.0.7)</small>


## [v0.0.6](https://github.com/tj-django/django-clone/releases/tag/v0.0.6) - 2019-11-10

<small>[Compare with v0.0.5](https://github.com/tj-django/django-clone/compare/v0.0.5...v0.0.6)</small>

### Added
- Added twine to deploy requirements ([59eba81](https://github.com/tj-django/django-clone/commit/59eba81e23cfb07687ae2c1b01ce82573597f61a) by Tonye Jack).


## [v0.0.5](https://github.com/tj-django/django-clone/releases/tag/v0.0.5) - 2019-11-10

<small>[Compare with v0.0.3](https://github.com/tj-django/django-clone/compare/v0.0.3...v0.0.5)</small>

### Added
- Added the changelog.md ([3e6aeb2](https://github.com/tj-django/django-clone/commit/3e6aeb2307fe5a29b9e68fd1acac1ae5e3cfe974) by Tonye Jack).


## [v0.0.3](https://github.com/tj-django/django-clone/releases/tag/v0.0.3) - 2019-11-10

<small>[Compare with v0.0.1](https://github.com/tj-django/django-clone/compare/v0.0.1...v0.0.3)</small>

### Added
- Add class variable use_unique_duplicate_suffix ([fd207c4](https://github.com/tj-django/django-clone/commit/fd207c41398a469ebca01bbe7ad7c0284a54d218) by Andres Portillo).
- Added new line at the end of the file. ([b5b68fc](https://github.com/tj-django/django-clone/commit/b5b68fc139e5c708c5f370fc4b3256d31d1daefc) by Tonye Jack).
- Added new line. ([4327dab](https://github.com/tj-django/django-clone/commit/4327dab28b06a0efec071eb4822bc916945399dc) by Tonye Jack).
- Added create_copy_of_instance utility. ([ab41b02](https://github.com/tj-django/django-clone/commit/ab41b02f1b52cf8f4ca6b7452085f66e69f25bb7) by Tonye Jack).
- Add django-admin clonablemodeladmin ([147c56f](https://github.com/tj-django/django-clone/commit/147c56fa59f770278050eeecf0868a611a15e060) by Sebastian Kindt).

### Changed
- Change comparison to check for any truthy value ([6d11bd1](https://github.com/tj-django/django-clone/commit/6d11bd1ae43d395ec08e6764cdf7cff597b79f54) by Andres Portillo).
- Changed docker image. ([9644e73](https://github.com/tj-django/django-clone/commit/9644e73e4682904df818e678484971edb5118990) by Tonye Jack).

### Fixed
- Fix admin url regex ([e806e97](https://github.com/tj-django/django-clone/commit/e806e97bcbaec9f3030db97f6afce4ff9700619e) by Tonye Jack).
- Fixed test. ([d7cc014](https://github.com/tj-django/django-clone/commit/d7cc014c7b7547863865bdb98b1e8c7d2b32d75d) by Tonye Jack).
- Fix clone of one to many and many to one ([78a506b](https://github.com/tj-django/django-clone/commit/78a506b6caff3a7715f35a617f96c56bf2087028) by Sebastian Kindt).
- Fixed install command. ([1ea325c](https://github.com/tj-django/django-clone/commit/1ea325c2981a22f62b2c52011a3c77d82c2c77c5) by Tonye Jack).
- Fixed virtualenv. ([eab8da9](https://github.com/tj-django/django-clone/commit/eab8da905bd110e7d8bffe4b1bb680c45caa8d75) by Tonye Jack).

### Removed
- Removed extra spaces. ([28f327f](https://github.com/tj-django/django-clone/commit/28f327fbdf129e5477dc200f8af822a10a4867a0) by Tonye Jack).
- Remove redundant one to one clone. ([d1a56bd](https://github.com/tj-django/django-clone/commit/d1a56bdc1c7f000b5729b7c13324077e1b2a7267) by Tonye Jack).
- Removed unused code. ([6216032](https://github.com/tj-django/django-clone/commit/6216032d67534f0ab35da8efb574a6c1aebcf838) by Tonye Jack).


## [v0.0.1](https://github.com/tj-django/django-clone/releases/tag/v0.0.1) - 2019-04-06

<small>[Compare with first commit](https://github.com/tj-django/django-clone/compare/7b01ca1df72d4ac2a691257807cf9eab426332ae...v0.0.1)</small>

### Added
- Added pypi deployment setup. ([96816e6](https://github.com/tj-django/django-clone/commit/96816e66ca00d6146860cb96e64047d8f5add6d8) by Tonye Jack).
- Added circleci config. ([af22fc8](https://github.com/tj-django/django-clone/commit/af22fc8c00fdb17f12d83140c35a50cd8c678ba9) by Tonye Jack).
- Added base class setup. ([7b01ca1](https://github.com/tj-django/django-clone/commit/7b01ca1df72d4ac2a691257807cf9eab426332ae) by Tonye Jack).

### Fixed
- Fixed typo. ([1cfe037](https://github.com/tj-django/django-clone/commit/1cfe037e50c8fca6c31a31ecf4b36b7c88c39fbe) by Tonye Jack).


