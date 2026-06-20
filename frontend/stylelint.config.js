export default {
  extends: ['stylelint-config-standard-scss'],
  rules: {
    'selector-class-pattern': [
      '^([a-z][a-z0-9]*)(-[a-z0-9]+)*$|^Mui[a-zA-Z0-9-]+$',
      {
        message: 'Expected class selector to be kebab-case or a valid Mui class name',
        resolveNestedSelectors: true,
      },
    ],
  },
};