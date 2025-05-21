import React from 'react';
import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import store from './redux/store';

jest.mock('mui-react-hook-form-plus', () => ({
  HookTextField: () => null,
  HookSelect: () => null,
  HookDatePicker: () => null,
  HookDateTimePicker: () => null,
  HookTimePicker: () => null,
  useHookForm: jest.fn(),
}), { virtual: true });

jest.mock('./components/forms/FormContainer', () => ({
  WrappedRegistrationForm: () => <div />,
  WrappedResyTokenForm: () => <div />,
  WrappedResyResRequestForm: () => <div />,
  WrappedPasswordResetForm: () => <div />,
  WrappedRegisterVenueForm: () => <div />,
  WrappedSignInForm: () => <div />,
  WrappedBugReportForm: () => <div />,
}));

jest.mock('./components/user/Profile', () => () => <div />);
jest.mock('./components/ErrorPage', () => () => <div />);
jest.mock('./components/user/CheckResyToken', () => () => <div />);
jest.mock('./components/Navbar', () => () => <div />);
import App from './App';

jest.mock('./firebase', () => ({
  auth: { onAuthStateChanged: (cb) => { cb(null); return () => {}; } },
  getResyToken: jest.fn(),
}));

test('renders private mode message on home page', () => {
  render(
    <Provider store={store}>
      <App />
    </Provider>
  );
  expect(
    screen.getByText(/Currently in private mode, please login or register for access/i)
  ).toBeInTheDocument();
});
