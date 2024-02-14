# Copyright (c) 2021 rdbende <rdbende@gmail.com>

# The Azure theme is a beautiful modern ttk theme inspired by Microsoft's fluent design.

package require Tk 8.6

namespace eval ttk::theme::azure-dark {
    variable version 2.0
    package provide ttk::theme::azure-dark $version

    ttk::style theme create azure-dark -parent vista -settings {
        proc load_images {imgdir} {
            variable I
            foreach file [glob -directory $imgdir *.png] {
                set img [file tail [file rootname $file]]
                set I($img) [image create photo -file $file -format png]
            }
        }

        load_images [file join [file dirname [info script]] dark]

        array set colors {
            -fg             "#ffffff"
            -bg             "#242424"
            -disabledfg     "#aaaaaa"
            -disabledbg     "#737373"
            -selectfg       "#ffffff"
            -selectbg       "#007fff"
            -sidebarbg      "#2b2b2b"
            -hoverbg        "#3d3d3d"
        }

        ttk::style layout TButton {
            Button.button -children {
                Button.padding -children {
                    Button.label -side left -expand true
                }
            }
        }

        ttk::style layout TCheckbutton {
            Checkbutton.button -children {
                Checkbutton.padding -children {
                    Checkbutton.indicator -side left
                    Checkbutton.label -side right -expand true
                }
            }
        }

        ttk::style layout Switch.TCheckbutton {
            Switch.button -children {
                Switch.padding -children {
                    Switch.indicator -side left
                    Switch.label -side right -expand true
                }
            }
        }

        ttk::style layout TCombobox {
            Combobox.field -sticky nswe -children {
                Combobox.padding -expand true -sticky nswe -children {
                    Combobox.textarea -sticky nswe
                }
            }
            Combobox.button -side right -sticky ns -children {
                Combobox.arrow -sticky nsew
            }
        }

        ttk::style layout TSpinbox {
            Spinbox.field -sticky nsew -children {
                Spinbox.padding -expand true -sticky nswe -children {
                    Spinbox.textarea -sticky nswe
                }

            }
            Spinbox.button -side right -sticky ns -children {
                null -side right -children {
                    Spinbox.uparrow -side top
                    Spinbox.downarrow -side bottom
                }
            }
        }

        ttk::style layout TLabelframe {
            Labelframe.border {
                Labelframe.padding -expand 1 -children {
                    Labelframe.label -side right
                }
            }
        }


        # Elements

        # Button
        ttk::style configure TButton -padding {8 4 8 4} -width -10 -anchor center

        ttk::style map TButton -background [list \
            	{selected disabled} $colors(-sidebarbg) \
                disabled $colors(-sidebarbg) \
                pressed $colors(-sidebarbg) \
                selected $colors(-sidebarbg) \
                active $colors(-sidebarbg) \
                focus $colors(-sidebarbg) \
        ]

        ttk::style element create Button.button image \
            [list $I(rect-basic) \
            	{selected disabled} $I(rect-basic) \
                disabled $I(rect-basic) \
                pressed $I(rect-basic) \
                selected $I(rect-basic) \
                active $I(button-hover) \
                focus $I(button-hover) \
            ] -border 4 -sticky ewns

        # Checkbutton
        ttk::style configure TCheckbutton -padding 4

        ttk::style map TCheckbutton -foreground \
            [list disabled $colors(-disabledfg)]

        ttk::style element create Checkbutton.indicator image \
            [list $I(box-basic) \
                {selected disabled} $I(check-basic) \
                disabled $I(box-disabled) \
                {pressed selected} $I(check-hover) \
                {active selected} $I(check-hover) \
                selected $I(check-accent) \
                {pressed !selected} $I(rect-hover) \
                active $I(box-hover) \
            ] -width 26 -sticky w

        # Entry

        ttk::style map Entry.field -background [list \
            {!focus} $colors(-sidebarbg) \
            readonly $colors(-sidebarbg) \
            {readonly hover} $colors(-sidebarbg) \
            {readonly focus} $colors(-sidebarbg) \
        ]

        # Combobox
        ttk::style map TCombobox -background [list \
            {!focus} $colors(-sidebarbg) \
            {readonly hover} $colors(-sidebarbg) \
            {readonly focus} $colors(-sidebarbg) \
        ]

        ttk::style map TCombobox -selectbackground [list \
            {!focus} $colors(-selectbg) \
            {readonly hover} $colors(-selectbg) \
            {readonly focus} $colors(-selectbg) \
        ]

        ttk::style map TCombobox -selectforeground [list \
            {!focus} $colors(-selectfg) \
            {readonly hover} $colors(-selectfg) \
            {readonly focus} $colors(-selectfg) \
        ]

        ttk::style element create Combobox.field \
            image [list $I(box-basic) \
                {readonly disabled} $I(rect-basic) \
                {readonly pressed} $I(rect-basic) \
                {readonly focus hover} $I(button-hover) \
                {readonly hover} $I(button-hover) \
            ] -border 5 -padding {8}

        ttk::style element create Combobox.button \
            image [list $I(combo-button-basic) \
                 {readonly hover} $I(combo-button-hover)
            ] -border 5 -padding {2 6 6 6}

        ttk::style element create Combobox.arrow image $I(down) \
            -width 15 -sticky e

        # Spinbox
        ttk::style element create Spinbox.field \
            image [list $I(box-basic) \
                invalid $I(box-invalid) \
                disabled $I(box-basic) \
                focus $I(box-accent) \
                hover $I(box-hover) \
            ] -border 5 -padding {8 4 8 4} -sticky news

        ttk::style element create Spinbox.uparrow \
            image [list $I(up) \
                disabled $I(up) \
                pressed $I(up-accent) \
                active $I(up-accent) \
            ] -border 4 -padding {-8} -width 15 -sticky e

        ttk::style element create Spinbox.downarrow \
            image [list $I(down) \
                disabled $I(down) \
                pressed $I(down-accent) \
                active $I(down-accent) \
            ] -border 4 -padding {-8} -width 15 -sticky e

        ttk::style element create Spinbox.button \
            image [list $I(combo-button-basic) \
                 {!readonly focus} $I(combo-button-focus) \
                 {readonly focus} $I(combo-button-hover) \
                 {readonly hover} $I(combo-button-hover)
            ] -border 5 -padding {2 5 5 5}

        # Labelframe
        ttk::style element create Labelframe.border image $I(card) \
            -border 5 -padding 4 -sticky news
    }
}
