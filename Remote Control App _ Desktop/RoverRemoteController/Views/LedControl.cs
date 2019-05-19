//////////////////////////////////
// Rover Remote Controller      //
//                              //
// Smallrobots.it 2019          //
//                              //
// Happily shared under the     //
// MIT Licence                  //
//////////////////////////////////
///
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;

namespace RoverRemoteController.Views
{
    /// <summary>
    /// Led control
    /// </summary>
    public class LedControl : CheckBox
    {
        static LedControl()
        {
            DefaultStyleKeyProperty.OverrideMetadata(typeof(LedControl), new FrameworkPropertyMetadata(typeof(LedControl)));
        }

        public static readonly DependencyProperty OnColorProperty =
            DependencyProperty.Register("OnColor", typeof(Brush), typeof(LedControl), new PropertyMetadata(Brushes.Green));

        public Brush OnColor
        {
            get { return (Brush)GetValue(OnColorProperty); }
            set { SetValue(OnColorProperty, value); }
        }

        public static readonly DependencyProperty OffColorProperty =
            DependencyProperty.Register("OffColor", typeof(Brush), typeof(LedControl), new PropertyMetadata(Brushes.Red));

        public Brush OffColor
        {
            get { return (Brush)GetValue(OffColorProperty); }
            set { SetValue(OffColorProperty, value); }
        }
    }
}
