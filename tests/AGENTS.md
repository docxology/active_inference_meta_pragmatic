# Test guidance

All tests use real data, computations and temporary filesystem artifacts. Never use MagicMock, mocker.patch, unittest.mock or a mocking framework.

Test categorical support, asymmetric transitions, soft evidence, numerical identities, invalid inputs, matched statistical units and actual workflow artifacts. A test proving an old scientifically incorrect behavior should be corrected with an explicit analytical expectation; do not merely weaken assertions to obtain a pass.

The repository coverage gate is 90% with a 95% target. The pipeline integration test may use a longer explicit timeout because it writes real multi-format figures. CI must include manuscript validation, reproduction and package/script smoke checks in addition to unit tests.
