//
//  LoginViewController.swift
//  FWB POS
//
//  Created by Ben Grass on 4/3/15.
//  Copyright (c) 2015 Barsoft. All rights reserved.
//

import UIKit

class LoginViewController: UIViewController, UITextFieldDelegate {
    var usernameField: UITextField!
    var passwordField: UITextField!
    var signInButton: UIButton!
    var sender: ViewController!

    func setUISender(_ sender: ViewController) {
        self.sender = sender
    }
    
    
    override func viewDidLoad() {
        
        super.viewDidLoad()
        self.view.backgroundColor = UIColor(red: 173.0/255.0, green: 244.0/255.0, blue: 247.0/255.0, alpha: 1)
        let yDist = 0.05 * self.view.frame.size.height
        var textFieldHeight: CGFloat = 30.0
        if(UIDevice.current.userInterfaceIdiom == UIUserInterfaceIdiom.pad) {
            textFieldHeight = 60.0
        }
        usernameField = UITextField(frame: CGRect(x: 51.0, y: 0.1 * self.view.frame.size.height, width: self.view.frame.size.width - 102, height: textFieldHeight))
        usernameField.placeholder = "Store PIN"
        usernameField.backgroundColor = #colorLiteral(red: 1, green: 1, blue: 1, alpha: 1)
        usernameField.borderStyle = .roundedRect
        usernameField.autocorrectionType = .no
        usernameField.autocapitalizationType = .none
        usernameField.adjustsFontSizeToFitWidth = true
        usernameField.keyboardType = .numberPad
        usernameField.keyboardAppearance = .dark
        usernameField.returnKeyType = .next
        usernameField.delegate = self
        self.view.addSubview(usernameField)
        
        passwordField = UITextField(frame: CGRect(x: 51.0, y: usernameField.frame.size.height + yDist + usernameField.frame.origin.y, width: self.view.frame.size.width - 102, height: textFieldHeight))
        passwordField.placeholder = "Password"
        passwordField.backgroundColor = #colorLiteral(red: 1, green: 1, blue: 1, alpha: 1)
        passwordField.borderStyle = .roundedRect
        passwordField.autocorrectionType = .no
        passwordField.autocapitalizationType = .none
        passwordField.adjustsFontSizeToFitWidth = true
        passwordField.keyboardAppearance = .dark
        passwordField.returnKeyType = .done
        passwordField.delegate = self
        passwordField.isSecureTextEntry = true
        self.view.addSubview(passwordField)

        var mainLabelTextSize: CGFloat = 20
        if(UIDevice.current.userInterfaceIdiom == .pad) {
            mainLabelTextSize = 40
        }

        signInButton = UIButton(frame: CGRect(x: 0.25 * self.view.frame.size.width, y: passwordField.frame.origin.y + passwordField.frame.size.height + yDist, width: 0.5 * self.view.frame.size.width, height: 2 * textFieldHeight))
        signInButton.setTitle("Sign In", for: UIControlState())
        signInButton.setTitleColor(UIColor.white, for: UIControlState())
        signInButton.titleLabel!.font = UIFont.boldSystemFont(ofSize: mainLabelTextSize)
        signInButton.backgroundColor = UIColor(white: 0, alpha: 0.3)
        signInButton.layer.cornerRadius = 10
        signInButton.layer.borderWidth = 3.25
        signInButton.layer.borderColor = UIColor.white.cgColor
        signInButton.addTarget(sender, action: Selector(("login:")), for: .touchUpInside)
        self.view.addSubview(signInButton!)

    }
    

    func textFieldShouldReturn(_ textField: UITextField) -> Bool {
        if usernameField.isFirstResponder {
            usernameField.resignFirstResponder()
            passwordField.becomeFirstResponder()
        } else if passwordField.isFirstResponder {
            passwordField.resignFirstResponder()
            self.sender.login(signInButton)
        }
        return true
    }
    
    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        for object in self.view.subviews {
            if let o = object as? UITextField {
                if o.isFirstResponder {
                    o.resignFirstResponder()
                }
            }
        }
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
    }
    
}
