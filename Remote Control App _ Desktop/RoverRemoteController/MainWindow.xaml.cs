//////////////////////////////////
// Rover Remote Controller      //
//                              //
// Smallrobots.it 2019          //
//                              //
// Happily shared under the     //
// MIT Licence                  //
//////////////////////////////////

using System;
using System.Windows;
using System.Windows.Input;
using RoverRemoteController.Views;

namespace RoverRemoteController
{
    /// <summary>
    /// Logica di interazione per MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
        }

        /// <summary>
        /// Move the window when mouse is down on Canvas
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void Canvas_MouseDown(object sender, MouseButtonEventArgs e)
        {
            this.DragMove();
        }

        /// <summary>
        /// Minimize the window
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void Minimize_Button_Click(object sender, RoutedEventArgs e)
        {
            WindowState = WindowState.Minimized;
        }

        /// <summary>
        /// Close the app
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void Close_Button_Click(object sender, RoutedEventArgs e)
        {
            Close();
        }

        /// <summary>
        /// Intercept window state changes
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void Window_StateChanged(object sender, EventArgs e)
        {
            switch (this.WindowState)
            {
                case WindowState.Maximized:
                    break;
                case WindowState.Minimized:
                    break;
                case WindowState.Normal:
                    break;
            }
        }

        /// <summary>
        /// It ignores the click, because the control is used just as a readonly indicator
        /// </summary>
        private void OnlineIndicator_Click(object sender, RoutedEventArgs e)
        {
            ((LedControl)sender).IsChecked = !((LedControl)sender).IsChecked;
        }
    }

}