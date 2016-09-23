//
//  ViewController.swift
//  FWB POS
//
//  Created by Ben Grass on 3/29/15.
//  Copyright (c) 2015 Barsoft. All rights reserved.
//

//TODO, KEYBOARD FUNCTIONALITY STUFF, DISMISSING BY PRESSING BLANK SPACE, ETC. LEGGO BAYBEE

import UIKit
import Alamofire
import SwiftyJSON

fileprivate func < <T : Comparable>(lhs: T?, rhs: T?) -> Bool {
  switch (lhs, rhs) {
  case let (l?, r?):
    return l < r
  case (nil, _?):
    return true
  default:
    return false
  }
}

fileprivate func <= <T : Comparable>(lhs: T?, rhs: T?) -> Bool {
  switch (lhs, rhs) {
  case let (l?, r?):
    return l <= r
  default:
    return !(rhs < lhs)
  }
}


class ViewController: UIViewController, UITextFieldDelegate {
    
    var mainLabel: UILabel? = nil
    var logoImage: UIImage? =  nil
    var promoText: String? = nil
    var backgroundColor: UIColor? = nil
    var highlightColor: UIColor? = nil
    var logoImageView: UIImageView? = nil
    var userCredentialField: UITextField? = nil
    var accountTypeController: UISegmentedControl? = nil
    var loginButton : UIButton? = nil
    var showSignUpScreenButton: UIButton? = nil
    var cancelLoginButton: UIButton? = nil
    var fullNameField: UITextField? = nil
    var signUpButton: UIButton? = nil
    var cancelSignUpButton: UIButton? = nil
    var promoTextLabel: UILabel? = nil
    var canSpamLabel: UILabel? = nil
    var showLoginScreenButton: UIButton? = nil
    var redeemCouponButton: UIButton? = nil
    // scanner view
    var accountTypePhone: Bool = true
    var isSigningUp: Bool = false
    var username: String? = nil
    var password: String? = nil
    var storeName: String!
    var opaqueColor = UIColor(white: 0, alpha: 0.3)
    var tag = 0
    var login: LoginViewController? = nil
    var selectCodeController: SelectCodeViewController? = nil
    var autoRotate = true
    var IP: String!
    var useDollars: Bool!
    
    //
    // SET UP AND MEMORY - preload setup and memory warning control
    //
    override func viewDidLoad() {
        super.viewDidLoad()
        startUp()
        // Do any additional setup after loading the view, typically from a nib.
    }
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        
        // Dispose of any resources that can be recreated.
    }
    override var prefersStatusBarHidden : Bool {
        return true
    }
    override var shouldAutorotate : Bool {
        return autoRotate
    }

    //
    // FUNCTIONALITY - actual protocol, uses networking methods to make things happen
    //
    func addPoints(_ target: String, type: Int, dollars: Double) {
        
        let params: Dictionary<String, AnyObject> = ["username": username! as AnyObject, "password": password! as AnyObject, "ctype": 2 as AnyObject, "reqtype": "addpoints" as AnyObject, "tag": (tag =  tag + 1) as AnyObject, "target": target as AnyObject, "type": type as AnyObject, "dollars": dollars as AnyObject]
        //print(params)
        request("\(IP)/api/gateway", method: .post, parameters: params, encoding: JSONEncoding.default)
            .responseJSON { response in
                if let x = response.result.value {
                    let results = JSON(x)
                    let code = results["code"].intValue
                    if(code/100 == 2) {
                        let name = results["name"].stringValue
                        var offers: Array<(String, String, Int, Int)> = []
                        let points = results["points"].intValue
                        let id = results["id"].intValue
                        for x in results["offers"].arrayValue {
                            let offerName = x["name"].stringValue
                            let offerDesc = x["desc"].stringValue
                            let offerPoints = x["points"].intValue
                            let offerID = x["id"].intValue
                            let tuple = (offerName, offerDesc, offerPoints, offerID)
                            offers.append(tuple)
                        }
                        if offers.count == 1 && points - offers[0].2 >= 0 {
                            self.showOfferSelected(id, name: offers[0].0, id: offers[0].3)
                        } else if offers.count > 1 {
                            var count = 0
                            for o in offers {
                                if points - o.2 >= 0 {
                                    count += 1
                                }
                            }
                            if count > 0 {
                                self.showOffers(offers, name: name, points: points, target: id)
                            } else {
                                self.showPoints(name, points: points)
                            }
                            
                        } else {
                            self.showPoints(name, points: points)
                        }
                    } else if code == 401 {
                        self.showStatus("Invalid Credentials")
                    } else if code == 403 {
                        self.showStatus("Please wait longer before trying again.")
                    } else if code == 418 {
                        self.showStatus("The server is teapot.")
                    } else {
                        self.showStatus("Oops, we have encountered an error!")
                    }
                    
                } else {
                    //println("ADDPOINTS ERROR")
                    //print(req.description)
                    self.showStatus("Oops, it looks like we have encountered a network error!")
                }
        }
    }
    func createAccount(_ newTarget: String, type: Int, fullName: String, dollars: Double) {
        let params: Dictionary<String, AnyObject> = ["username": newTarget as AnyObject, "password": "~" as AnyObject, "fullname": fullName as AnyObject, "ctype": 2 as AnyObject, "reqtype": "signup" as AnyObject, "tag": (tag = tag + 1) as AnyObject, "type": type as AnyObject]
        request("\(IP)/api/gateway", method: .post, parameters: params, encoding: JSONEncoding.default)
            .responseJSON { response in
                    
                if let x = response.result.value {
                    let results = JSON(x)
                    let code = results["code"].intValue
                    if(code/100 == 2) {
                        self.addPoints(newTarget, type: type, dollars: dollars)
                    } else if code == 401 && self.accountTypePhone {
                        self.showStatus("Invalid Phone Number, Try Again")
                    } else if code == 401 && !self.accountTypePhone{
                        self.showStatus("Invalid E-mail, Try Again")
                    } else if code == 400 {
                        self.showStatus("Account Already Exists")
                    } else {
                        self.showStatus("Oops, it looks like we have encountered an error!")
                    }

                } else {
                    //print(error!.description)
                    //print("CREATE ACCOUNT ERROR")
                    self.showStatus("Oops, it looks like we have encountered a network error!")
                }
                    

        }
    }
    func selectOffer(_ target: Int, id: Int) {
        if let controller = selectCodeController {
            controller.dismiss(animated: true, completion: { () -> Void in
                self.selectCodeController = nil
                self.willAutorotate(true)
            })
        }
        let params: Dictionary<String, AnyObject> = ["username": username! as AnyObject, "password": password! as AnyObject, "ctype": 2 as AnyObject, "reqtype": "makecode" as AnyObject, "tag": (tag = tag + 1) as AnyObject, "target": target as AnyObject, "id": id as AnyObject]
        request("\(IP)/api/gateway", method: .post, parameters: params, encoding: JSONEncoding.default)
            .responseJSON { response in
               
                if let x = response.result.value {
                    let results = JSON(x)

                    let code = results["code"].intValue
                    if code/100 == 2 {
                        let points = results["points"].intValue
                        var pointString = "points"
                        if points == 1 {
                            pointString = "point"
                        }
                        let status = "We have sent you a coupon code! You now have \(points) \(pointString)."
                        self.showStatus(status)
                    } else {
                        self.showStatus("Oops, it looks like we have encountered an error!")
                    }
                } else {
                    //print("SELECTOFFER ERROR")
                    self.showStatus("Oops, it looks like we have encountered a network error!")
                }
                    
        }

    }
    func useCode(_ pin: Int, code: Int) {
        let params: Dictionary<String, AnyObject> = ["username": username! as AnyObject, "password": password! as AnyObject, "ctype": 2 as AnyObject, "reqtype": "usecode" as AnyObject, "tag": (tag = tag + 1) as AnyObject, "id": pin as AnyObject, "code": code as AnyObject]
        request("\(IP)/api/gateway", method: .post, parameters: params, encoding: JSONEncoding.default)
            .responseJSON { response in
          
                    
                if let x = response.result.value {
                    let results = JSON(x)
                    let code = results["code"].intValue
                    if(code/100 == 2) {
                        let offer = results["offer"].stringValue
                        let alert = UIAlertView(title: "Offer Redeemed", message: offer, delegate: nil, cancelButtonTitle: "Okay")
                        alert.show()
                    } else if code == 401 {
                        // incorrect pin
                        let alert = UIAlertView(title: "Error", message: "Incorrect PIN", delegate: nil, cancelButtonTitle: "Okay")
                        alert.show()
                    } else if code == 404 {
                        // code DNE
                        let alert = UIAlertView(title: "Error", message: "Code Does Not Exist", delegate: nil, cancelButtonTitle: "Okay")
                        alert.show()
                    } else if code == 403 {
                        let alert = UIAlertView(title: "Error", message: "Code Not Valid at this Store", delegate: nil, cancelButtonTitle: "Okay")
                        alert.show()
                    } else if code == 410 {
                        // code expired
                        let alert = UIAlertView(title: "Error", message: "Code Has Expired", delegate: nil, cancelButtonTitle: "Okay")
                        alert.show()
                    } else {
                        let alert = UIAlertView(title: "Error", message: "Invalid Code", delegate: nil, cancelButtonTitle: "Okay")
                        alert.show()
                    }
                    
                } else {
                    let alert = UIAlertView(title: "Error", message: "Oops, we have encountered a network error.", delegate: nil, cancelButtonTitle: "Okay")
                    alert.show()
                }
                
                
        }
    }
    func validateLogin(_ username: String, password: String) {
        let params: Dictionary<String, AnyObject> = ["username": username as AnyObject, "password": password as AnyObject, "ctype": 2 as AnyObject, "reqtype": "validate" as AnyObject, "tag": (tag = tag + 1) as AnyObject]
        request("https://fwbapp.com/api/gateway", method: .post, parameters: params, encoding: JSONEncoding.default)
            .responseJSON { response in
                
                if let x = response.result.value {
                    let results = JSON(x)
                    let code = results["code"].intValue
                    if(code/100 == 2) {
                        if let ip = results["IP"].string {
                            self.IP = ip
                        } else {
                            self.IP = "https://www.fwbapp.com"
                        }
                        self.username = self.login!.usernameField.text
                        self.password = self.login!.passwordField.text
                        self.login!.view.removeFromSuperview()
                        self.login = nil
                        self.setUp()
                    } else {
                        let incorrectAlert = UIAlertController(title: "Error", message: "Invalid Credentials, Please Try Again.", preferredStyle: .alert)
                        incorrectAlert.addAction(UIAlertAction(title: "Done", style: UIAlertActionStyle.default, handler: nil))
                        self.login!.usernameField.resignFirstResponder()
                        self.login!.passwordField.resignFirstResponder()
                        self.login!.present(incorrectAlert, animated: true, completion: { () -> Void in
                            self.login!.signInButton.isEnabled = true
                        })
                        self.login!.usernameField.text = ""
                        self.login!.passwordField.text = ""
                        
                    }
                } else {
                    let incorrectAlert = UIAlertController(title: "Error", message: "Ooops, We've encountered a network error.", preferredStyle: .alert)
                    incorrectAlert.addAction(UIAlertAction(title: "Done", style: UIAlertActionStyle.default, handler: nil))
                    self.login!.usernameField.resignFirstResponder()
                    self.login!.passwordField.resignFirstResponder()
                    self.login!.present(incorrectAlert, animated: true, completion: { () -> Void in
                        self.login!.signInButton.isEnabled = true
                    })
                    self.login!.usernameField.text = ""
                    self.login!.passwordField.text = ""
                    
            
                }
        }

    }
    func fetchGraphicalElements() {
        let params: Dictionary<String, AnyObject> = ["username": username! as AnyObject, "password": password! as AnyObject, "ctype": 2 as AnyObject, "reqtype": "getbrand" as AnyObject, "tag": (tag = tag + 1) as AnyObject]
        
        request("\(IP)/api/gateway", method: .post, parameters: params, encoding: JSONEncoding.default)
            .responseJSON { response in
                
                if let x = response.result.value {
                    let results = JSON(x)
                    let code = results["code"].intValue
                    if(code/100 == 2) {
                        self.promoText = results["promo"].stringValue
                        let br = CGFloat(results["color"][0].doubleValue)
                        let bg = CGFloat(results["color"][1].doubleValue)
                        let bb = CGFloat(results["color"][2].doubleValue)
                        self.backgroundColor = UIColor(red: br/255.0, green:bg/255.0, blue:bb/255.0, alpha:1)
                        let hr = CGFloat(results["highlight"][0].doubleValue)
                        let hg = CGFloat(results["highlight"][1].doubleValue)
                        let hb = CGFloat(results["highlight"][2].doubleValue)
                        self.highlightColor = UIColor(red: hr/255.0, green:hg/255.0, blue:hb/255.0, alpha:1)
                        let fileName = results["logo"].stringValue
                        let stringURL = "\(self.IP)/api/assets/\(fileName)"
                        let url = URL(string: stringURL)
                        var logoData = try? Data(contentsOf: url!)
                        self.logoImage = UIImage(data: logoData!)
                        self.storeName = results["name"].stringValue
                        self.useDollars = results["dollars"].boolValue
                        self.setUpUIElements()
                        self.statusToScanner()
                    } else {
                        self.showStatus("Error. Please reopen app.")
                    }
                    
                } else {
                    self.showStatus("Network Error. Please reopen app.")
                }
                
        }

        
    } // done

    
    
    
    //
    // GRAPICS FUNCTIONALITY - controls text field delegates and removing the keyboard, and setup
    //
    func login(_ sender: UIButton!) {
        self.login!.signInButton.isEnabled = false
        validateLogin(login!.usernameField.text!, password: login!.passwordField.text!)
    }
    func startUp() {
        willAutorotate(false)
        login = LoginViewController()
        login!.setUISender(self)
        view.addSubview(login!.view)
    }
    func setUp() {
        mainLabel = UILabel(frame: CGRect(x: 0.15*self.view.frame.size.width, y: 0.25*self.view.frame.size.height, width: 0.7*self.view.frame.size.width, height: 0.5*self.view.frame.size.height))
        mainLabel!.text = "Loading..."
        mainLabel!.textColor = #colorLiteral(red: 1, green: 1, blue: 1, alpha: 1)
        mainLabel!.font = UIFont.systemFont(ofSize: 34)
        mainLabel!.adjustsFontSizeToFitWidth = true
        mainLabel!.numberOfLines = 5
        mainLabel!.textAlignment = .center
        mainLabel!.lineBreakMode = .byWordWrapping
        mainLabel!.alpha = 0
        enableSubview(mainLabel!)
        self.view.addSubview(mainLabel!)
        self.view.backgroundColor = UIColor(red: 173.0/255.0, green: 244.0/255.0, blue: 247.0/255.0, alpha: 1)
        fetchGraphicalElements()
        

    }
    func willAutorotate(_ yes: Bool) {
        autoRotate = yes
        shouldAutorotate
    }
    func drawFrames(_ note: Notification?) {
        let yDist = 0.05 * self.view.frame.size.height
        var textFieldHeight: CGFloat = 30.0
        if(UIApplication.shared.keyWindow?.frame.size.height <= 320) {
            textFieldHeight = 25.0
        }
        if(UIDevice.current.userInterfaceIdiom == UIUserInterfaceIdiom.pad) {
            textFieldHeight = 60.0
        }
        var credentialHeight = 0.1 * self.view.frame.size.height
        let logoViewHeight = 0.25 * self.view.frame.size.height
        let logoViewWidth = logoViewHeight * (logoImage!.size.width/logoImage!.size.height)
        UIView.setAnimationCurve(UIViewAnimationCurve.easeIn)
        UIView.setAnimationDelegate(self)
        UIView.setAnimationDuration(0.25)
        
        mainLabel!.frame = CGRect(x: 0.15*self.view.frame.size.width, y: 0.25*self.view.frame.size.height, width: 0.7*self.view.frame.size.width, height: 0.5*self.view.frame.size.height)
        logoImageView!.frame = CGRect(x: (self.view.frame.size.width - logoViewWidth)/2, y: 0.07*self.view.frame.size.height, width: logoViewWidth, height: logoViewHeight)
        if(isSigningUp == false) {
            credentialHeight = 1.2 * yDist + logoImageView!.frame.size.height + logoImageView!.frame.origin.y
        }
        
        UIView.beginAnimations(nil, context: nil)

        userCredentialField!.frame = CGRect(x: 51.0, y: credentialHeight, width: 0.6 * (self.view.frame.size.width - 102), height: textFieldHeight)
        accountTypeController!.frame = CGRect(x: 51 + 0.65 * (self.view.frame.size.width - 102), y: userCredentialField!.frame.origin.y, width: 0.35*(self.view.frame.size.width - 102), height: textFieldHeight)
        loginButton!.frame = CGRect(x: self.view.frame.size.width/9, y: userCredentialField!.frame.size.height + (2*yDist) + userCredentialField!.frame.origin.y, width: self.view.frame.size.width/3, height: 2.5*textFieldHeight)
        showSignUpScreenButton!.frame = CGRect(x: 5*self.view.frame.size.width/9, y: userCredentialField!.frame.size.height + (2*yDist) + userCredentialField!.frame.origin.y, width: self.view.frame.size.width/3, height: 2.5*textFieldHeight)
        fullNameField!.frame = CGRect(x: 51, y: userCredentialField!.frame.size.height+yDist + userCredentialField!.frame.origin.y, width: self.view.frame.size.width - 102, height: textFieldHeight)
        signUpButton!.frame = CGRect(x: 0.25 * self.view.frame.size.width, y: fullNameField!.frame.origin.y + fullNameField!.frame.size.height + yDist, width: 0.5 * self.view.frame.size.width, height: 2 * textFieldHeight)
        cancelLoginButton!.frame = CGRect(x: self.view.frame.size.width - (0.01 * self.view.frame.size.height + 0.175*self.view.frame.size.height), y: self.view.frame.size.height * 0.915, width: self.view.frame.size.height*0.175, height: self.view.frame.size.height * 0.075)
        cancelSignUpButton!.frame = CGRect(x: self.view.frame.size.width/3, y: signUpButton!.frame.origin.y + signUpButton!.frame.size.height + yDist, width: self.view.frame.size.width/3, height: 1.5 * textFieldHeight)
        showLoginScreenButton!.frame = CGRect(x: self.view.frame.size.width - (0.01 * self.view.frame.size.height + 0.175*self.view.frame.size.height), y: self.view.frame.size.height * 0.915, width: self.view.frame.size.height*0.175, height: self.view.frame.size.height * 0.075)
        redeemCouponButton!.frame = CGRect(x: 0.01 * self.view.frame.size.height, y: 0.915 * self.view.frame.size.height, width: self.view.frame.size.height*0.175, height: self.view.frame.size.height * 0.075)
        promoTextLabel!.frame = CGRect(x: 0.2 * self.view.frame.size.width, y: (loginButton!.frame.origin.y + loginButton!.frame.size.height + redeemCouponButton!.frame.origin.y) * 0.5 - 0.1 * self.view.frame.size.height, width: 0.6 * self.view.frame.size.width, height: 0.2*self.view.frame.size.height)
        canSpamLabel!.frame = CGRect(x: 0.05*self.view.frame.size.width, y: 0.95*self.view.frame.size.height, width: 0.9*self.view.frame.size.width, height: 0.05*self.view.frame.size.height)
        
        UIView.commitAnimations()
        
    } // done
    func setUpUIElements() {
        willAutorotate(true)
        view.backgroundColor = backgroundColor
        // set up variables
        var mainLabelTextSize: CGFloat = 20
        var promoTextSize: CGFloat = 20
        if(UIDevice.current.userInterfaceIdiom == .pad) {
            mainLabelTextSize = 40
            promoTextSize = 30
        }
        // set up scanner
        
        //LABELS and IMAGE
        mainLabel!.textColor = highlightColor!

        canSpamLabel = UILabel()
        canSpamLabel!.text = "By signing up you are consenting to receiving communications from \(storeName)"
        canSpamLabel!.textColor = highlightColor!
        canSpamLabel!.font = UIFont.systemFont(ofSize: 10)
        canSpamLabel!.numberOfLines = 5
        canSpamLabel!.textAlignment = .center
        canSpamLabel!.lineBreakMode = .byWordWrapping
        canSpamLabel!.alpha = 0
        self.view.addSubview(canSpamLabel!)
        
        promoTextLabel = UILabel()
        promoTextLabel!.text = promoText
        promoTextLabel!.textColor = highlightColor!
        promoTextLabel!.font = UIFont.systemFont(ofSize: promoTextSize)
        promoTextLabel!.adjustsFontSizeToFitWidth = true
        promoTextLabel!.numberOfLines = 3
        promoTextLabel!.textAlignment = .center
        promoTextLabel!.lineBreakMode = .byWordWrapping
        promoTextLabel!.alpha = 0
        self.view.addSubview(promoTextLabel!)
        
        logoImageView = UIImageView(image: logoImage!)
        logoImageView!.alpha = 0
        self.view.addSubview(logoImageView!)
        
        
        //TEXT FIELDS
        userCredentialField = UITextField()
        userCredentialField!.placeholder = "Phone Number"
        userCredentialField!.backgroundColor = #colorLiteral(red: 1, green: 1, blue: 1, alpha: 1)
        userCredentialField!.borderStyle = .roundedRect
        userCredentialField!.keyboardType = .numberPad
        userCredentialField!.autocorrectionType = .no
        userCredentialField!.autocapitalizationType = .none
        userCredentialField!.adjustsFontSizeToFitWidth = true
        userCredentialField!.keyboardAppearance = .dark
        userCredentialField!.delegate = self
        userCredentialField!.returnKeyType = .done
        userCredentialField!.addTarget(self, action: #selector(ViewController.autoFormatTextField), for:.editingChanged)
        userCredentialField!.alpha = 0
        userCredentialField!.isEnabled = false
        self.view.addSubview(userCredentialField!)
        
        fullNameField = UITextField()
        fullNameField!.placeholder = "Full Name"
        fullNameField!.backgroundColor = #colorLiteral(red: 1, green: 1, blue: 1, alpha: 1)
        fullNameField!.borderStyle = .roundedRect
        fullNameField!.autocorrectionType = .no
        fullNameField!.autocapitalizationType = .words
        fullNameField!.adjustsFontSizeToFitWidth = true
        fullNameField!.keyboardAppearance = .dark
        fullNameField!.delegate = self
        fullNameField!.returnKeyType = .done
        fullNameField!.alpha = 0
        fullNameField!.isEnabled = false
        self.view.addSubview(fullNameField!)
        
        //BUTTONS and CONTROL
        accountTypeController = UISegmentedControl(items: ["Phone", "Email"])
        accountTypeController!.selectedSegmentIndex = 0
        var controllerTextSize: CGFloat = 30
        if(UIDevice.current.userInterfaceIdiom == .phone) {
            controllerTextSize = 15
        }
        let font = UIFont.boldSystemFont(ofSize: controllerTextSize)
        let attributes = [NSFontAttributeName: font]
        accountTypeController!.setTitleTextAttributes(attributes, for: UIControlState())
        accountTypeController!.tintColor = highlightColor
        accountTypeController!.addTarget(self, action: #selector(ViewController.changeAccountType(_:)), for: .valueChanged)
        accountTypeController!.alpha = 0
        accountTypeController!.isEnabled = true
        self.view.addSubview(accountTypeController!)
        
        redeemCouponButton = UIButton()
        redeemCouponButton!.setTitle("Offer", for: UIControlState())
        redeemCouponButton!.setTitleColor(highlightColor, for: UIControlState())
        if(UIDevice.current.userInterfaceIdiom == .pad) {
            redeemCouponButton!.titleLabel?.font = UIFont.systemFont(ofSize: 17)
        }
        redeemCouponButton!.backgroundColor = opaqueColor
        redeemCouponButton!.layer.cornerRadius = 10
        redeemCouponButton!.addTarget(self, action: #selector(ViewController.redeemCouponHandler), for: .touchUpInside)
        redeemCouponButton!.layer.borderWidth = 2
        redeemCouponButton!.layer.borderColor = highlightColor!.cgColor
        redeemCouponButton!.alpha = 0
        redeemCouponButton!.isEnabled = false
        self.view.addSubview(redeemCouponButton!)
        
        showLoginScreenButton = UIButton()
        showLoginScreenButton!.setTitle("Login", for: UIControlState())
        showLoginScreenButton!.setTitleColor(highlightColor, for: UIControlState())
        if(UIDevice.current.userInterfaceIdiom == .pad) {
            showLoginScreenButton!.titleLabel?.font = UIFont.systemFont(ofSize: 17)
        }
        showLoginScreenButton!.backgroundColor = opaqueColor
        showLoginScreenButton!.layer.cornerRadius = 10
        showLoginScreenButton!.addTarget(self, action: #selector(ViewController.showLoginScreenHandler), for: .touchUpInside)
        showLoginScreenButton!.layer.borderWidth = 2
        showLoginScreenButton!.layer.borderColor = highlightColor!.cgColor
        showLoginScreenButton!.alpha = 0
        showLoginScreenButton!.isEnabled = false
        self.view.addSubview(showLoginScreenButton!)
        
        cancelLoginButton = UIButton()
        cancelLoginButton!.setTitle("Cancel", for: UIControlState())
        cancelLoginButton!.setTitleColor(highlightColor, for: UIControlState())
        if(UIDevice.current.userInterfaceIdiom == .pad) {
            cancelLoginButton!.titleLabel?.font = UIFont.systemFont(ofSize: 17)
        }
        cancelLoginButton!.backgroundColor = opaqueColor
        cancelLoginButton!.layer.cornerRadius = 10
        cancelLoginButton!.addTarget(self, action: #selector(ViewController.cancelLoginHandler), for: .touchUpInside)
        cancelLoginButton!.layer.borderWidth = 2
        cancelLoginButton!.layer.borderColor = highlightColor!.cgColor
        cancelLoginButton!.alpha = 0
        cancelLoginButton!.isEnabled = false
        self.view.addSubview(cancelLoginButton!)
        
        loginButton = UIButton()
        loginButton!.setTitle("Login", for: UIControlState())
        loginButton!.setTitleColor(highlightColor, for: UIControlState())
        loginButton!.titleLabel!.font = UIFont.boldSystemFont(ofSize: mainLabelTextSize)
        loginButton!.backgroundColor = opaqueColor
        loginButton!.layer.cornerRadius = 10
        loginButton!.addTarget(self, action: #selector(ViewController.getDollarsForLogin), for: .touchUpInside)
        loginButton!.layer.borderWidth = 3.25
        loginButton!.layer.borderColor = highlightColor!.cgColor
        loginButton!.alpha = 0
        loginButton!.isEnabled = false
        self.view.addSubview(loginButton!)
        
        showSignUpScreenButton = UIButton()
        showSignUpScreenButton!.setTitle("Sign Up", for: UIControlState())
        showSignUpScreenButton!.setTitleColor(highlightColor, for: UIControlState())
        showSignUpScreenButton!.titleLabel!.font = UIFont.boldSystemFont(ofSize: mainLabelTextSize)
        showSignUpScreenButton!.backgroundColor = opaqueColor
        showSignUpScreenButton!.layer.cornerRadius = 10
        showSignUpScreenButton!.addTarget(self, action: #selector(ViewController.showSignUpHandler), for: .touchUpInside)
        showSignUpScreenButton!.layer.borderWidth = 3.25
        showSignUpScreenButton!.layer.borderColor = highlightColor!.cgColor
        showSignUpScreenButton!.alpha = 0
        showSignUpScreenButton!.isEnabled = false
        self.view.addSubview(showSignUpScreenButton!)
        
        signUpButton = UIButton()
        signUpButton!.setTitle("Sign Up", for: UIControlState())
        signUpButton!.setTitleColor(highlightColor, for: UIControlState())
        signUpButton!.titleLabel!.font = UIFont.boldSystemFont(ofSize: mainLabelTextSize)
        signUpButton!.backgroundColor = opaqueColor
        signUpButton!.layer.cornerRadius = 10
        signUpButton!.addTarget(self, action: #selector(ViewController.getDollarsForSignUp), for: .touchUpInside)
        signUpButton!.layer.borderWidth = 3.25
        signUpButton!.layer.borderColor = highlightColor!.cgColor
        signUpButton!.alpha = 0
        signUpButton!.isEnabled = false
        self.view.addSubview(signUpButton!)
        
        cancelSignUpButton = UIButton()
        cancelSignUpButton!.setTitle("Cancel", for: UIControlState())
        cancelSignUpButton!.setTitleColor(highlightColor, for: UIControlState())
        cancelSignUpButton!.titleLabel!.font = UIFont.boldSystemFont(ofSize: 0.75 * mainLabelTextSize)
        cancelSignUpButton!.backgroundColor = opaqueColor
        cancelSignUpButton!.layer.cornerRadius = 10
        cancelSignUpButton!.addTarget(self, action: #selector(ViewController.cancelSignUpHandler), for: .touchUpInside)
        cancelSignUpButton!.layer.borderWidth = 3.25
        cancelSignUpButton!.layer.borderColor = highlightColor!.cgColor
        cancelSignUpButton!.alpha = 0
        cancelSignUpButton!.isEnabled = false
        self.view.addSubview(cancelSignUpButton!)
        
        UIDevice.current.beginGeneratingDeviceOrientationNotifications()
        NotificationCenter.default.addObserver(self, selector:#selector(ViewController.drawFrames(_:)), name: NSNotification.Name.UIDeviceOrientationDidChange, object: UIDevice.current)
        drawFrames(nil)
        
    } // done
    func autoFormatTextField() {
        if(accountTypePhone) {
            var myTextFieldSemaphore: Int? = nil
            let phoneNumberFormatter = PhoneNumberFormatter()
            let myLocale = "us"
            myTextFieldSemaphore = 0
            if myTextFieldSemaphore  != nil {
                myTextFieldSemaphore = 1
            }
            
            var phoneNumber: String = phoneNumberFormatter!.strip(userCredentialField!.text)
            
            if(phoneNumber.characters.count > 0) {
                var numOfCharsAllowed = 10;
                if(phoneNumber[phoneNumber.startIndex] == "1") {
                    numOfCharsAllowed = 11;
                }
                
                if(phoneNumber.characters.count  > numOfCharsAllowed) {
                    phoneNumber = phoneNumber.substring(to: phoneNumber.characters.index(phoneNumber.startIndex, offsetBy: numOfCharsAllowed));
                }
            }
            userCredentialField!.text = phoneNumberFormatter?.format(phoneNumber, withLocale: myLocale)
        }
    } // done
    func showOffers(_ offers: Array<(String, String, Int, Int)>, name: String, points: Int, target: Int) {
        willAutorotate(false)
        selectCodeController = SelectCodeViewController()
        selectCodeController!.setUp(offers, target: target, name: name, points: points, backgroundColor: backgroundColor!, highlightColor: highlightColor!, sender: self)
        self.present(selectCodeController!, animated: true, completion: nil)
    }
    func showPoints(_ name: String, points: Int) {
        var pointString = "points"
        if(points == 1) {
            pointString = "point"
        }
        changeLabelText("Hello, \(name)! You have \(points) \(pointString).")
        let delayInSeconds = 3.5
        let popTime = DispatchTime.now() + Double(Int64(delayInSeconds * Double(NSEC_PER_SEC))) / Double(NSEC_PER_SEC) // 1
        DispatchQueue.main.asyncAfter(deadline: popTime) {
            self.statusToScanner()
        }
    }
    func showStatus(_ status: String) {
        changeLabelText(status)
        let delayInSeconds = 3.5
        let popTime = DispatchTime.now() + Double(Int64(delayInSeconds * Double(NSEC_PER_SEC))) / Double(NSEC_PER_SEC) // 1
        DispatchQueue.main.asyncAfter(deadline: popTime) {
            self.statusToScanner()
        }
    }
    func showOfferSelected(_ target: Int, name: String, id: Int) {
        changeLabelText("You have received an offer for \"\(name)!\"")
        let delayInSeconds = 1.0
        let popTime = DispatchTime.now() + Double(Int64(delayInSeconds * Double(NSEC_PER_SEC))) / Double(NSEC_PER_SEC)
        DispatchQueue.main.asyncAfter(deadline: popTime, execute: { () -> Void in
            self.selectOffer(target, id: id)
        })
    }
    func didNotSelectOffer(_ name: String, points: Int) {
        selectCodeController!.dismiss(animated: true, completion: { () -> Void in
            self.selectCodeController = nil
            self.willAutorotate(true)
        })
        showPoints(name, points: points)
    }
    func textFieldShouldReturn(_ textField: UITextField) -> Bool {
        if userCredentialField!.isFirstResponder {
            userCredentialField!.resignFirstResponder()
            if fullNameField!.isEnabled == true {
                fullNameField!.becomeFirstResponder()
            } else {
                getDollarsForLogin()
            }
        } else if fullNameField!.isFirstResponder {
            fullNameField!.resignFirstResponder()
            getDollarsForSignUp()
        }
        return true
    } // done
    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        for object in self.view.subviews {
            if let o = object as? UITextField {
                if o.isFirstResponder {
                    o.resignFirstResponder()
                }
            }
        }
    }

    func changeAccountType(_ control: UISegmentedControl?) {
        if accountTypePhone == false && control!.selectedSegmentIndex == 0 {
            userCredentialField!.endEditing(true)
            userCredentialField!.keyboardType = .numberPad
            userCredentialField!.placeholder = "Phone Number"
            userCredentialField!.text = ""
            accountTypePhone = true
        } else if accountTypePhone == true && control!.selectedSegmentIndex == 1 {
            userCredentialField!.endEditing(true)
            userCredentialField!.keyboardType = .emailAddress
            userCredentialField!.placeholder = "Email"
            userCredentialField!.text = ""
            accountTypePhone = false
        }
    } // done
    func stripPhoneNumber(_ phoneNumber: String) -> String {
        let formatter = PhoneNumberFormatter()
        let strippedNumber: String = formatter!.strip(phoneNumber)
        var rawNumber: NSString? = nil
        if(strippedNumber.characters.count > 0 && strippedNumber[strippedNumber.startIndex] == "1") {
            rawNumber =  strippedNumber.substring(from: strippedNumber.characters.index(strippedNumber.startIndex, offsetBy: 1)) as NSString?
        } else {
            rawNumber = strippedNumber as NSString?
        }
        
        return rawNumber! as String
    } // done
    func disableSubview(_ subview: UIView) {
        if let button = subview as? UIButton {
            button.isEnabled = false
            button.alpha = 0
        } else if let textField = subview as? UITextField {
            textField.isEnabled = false
            textField.alpha = 0
            textField.text = ""
        } else if let control = subview as? UISegmentedControl {
            control.isEnabled = false
            control.alpha = 0
        } else {
            subview.alpha = 0
        }
    } // done
    func enableSubview(_ subview: UIView) {
        if let button = subview as? UIButton{
            button.isEnabled = true
            button.alpha = 1
            self.view.bringSubview(toFront: button)
        } else if let textField = subview as? UITextField {
            textField.isEnabled = true
            textField.alpha = 1
            self.view.bringSubview(toFront: textField)
        } else if let control = subview as? UISegmentedControl {
            control.isEnabled = true
            control.alpha = 1
            self.view.bringSubview(toFront: control)
        } else {
            subview.alpha = 1
            self.view.bringSubview(toFront: subview)
        }
        
        
        
    } //done
    func borderTextField(_ field: UITextField) {
        let components = backgroundColor!.cgColor.components
        field.layer.cornerRadius = 10
        field.layer.borderWidth = 4
        field.layer.borderColor = UIColor(red: 1.0 - (components?[0])!, green: 1.0 - (components?[1])!, blue: 1.0 - (components?[2])!, alpha: 1).cgColor

    }
    func deBorderTextField(_ field: UITextField) {
        field.layer.borderWidth = 0
        field.layer.borderColor = UIColor(white: 0, alpha: 0).cgColor
    }
    
    /*
    func textField(textField: UITextField, shouldChangeCharactersInRange range: NSRange, replacementString string: String) -> Bool {
    if string == "" {
    return true
    }
    let charSet = NSCharacterSet.symbolCharacterSet().invertedSet
    if string.rangeOfCharacterFromSet(charSet, options: nil, range: nil) == nil {
    return false
    } else {
    return true
    }
    } // PREVENTS EMOJIS (some of them at least)
    */
    
    
    //
    // BUTTON HANDLERS - responds to button presses, doing appropriate actions for labels, running things, etc.
    //
    func redeemCouponHandler() {
        let alert = UIAlertController(title: "Redeem Offer", message: "Input Offer Code", preferredStyle: .alert)
        alert.addTextField { (textField: UITextField!) -> Void in
            textField.placeholder = "Coupon Code"
            textField.keyboardAppearance = .dark
            textField.keyboardType = .numberPad
        }
        alert.addTextField { (textField: UITextField!) -> Void in
            textField.placeholder = "Store PIN"
            textField.isSecureTextEntry = true
            textField.keyboardType = .numberPad
            textField.keyboardAppearance = .dark
        }
        alert.addAction(UIAlertAction(title: "Cancel", style: .cancel, handler: nil))
        alert.addAction(UIAlertAction(title: "Redeem", style: .default, handler: { (action: UIAlertAction) -> Void in
            let pinField: UITextField = alert.textFields![1] 
            let codeField: UITextField = alert.textFields![0] 
            let pin = Int(pinField.text!)
            let code = Int(codeField.text!)
            
            if pin != nil && code != nil {
                self.useCode(Int(pinField.text!)!, code: Int(codeField.text!)!)
            } else {
                let alert = UIAlertView(title: "Error", message: "Please Fill In All Fields", delegate: nil, cancelButtonTitle: "Okay")
                alert.show()
            }
        }))
        present(alert, animated: true, completion: nil)
    }
    func showLoginScreenHandler() {
        scannerToLogin()
    }
    func cancelLoginHandler() {
        loginToScanner()
    }
    func loginHandler(_ dollars: Double) {

        if userCredentialField!.text == "" {
            borderTextField(userCredentialField!)
            let alert = UIAlertView(title: "Error", message: "Please enter your user credentials!", delegate: nil, cancelButtonTitle: "Okay")
            alert.show()
        } else if accountTypePhone && stripPhoneNumber(userCredentialField!.text!).characters.count < 10 {
            borderTextField(userCredentialField!)
            let alert = UIAlertView(title: "Error", message: "Please enter a valid phone number!", delegate: nil, cancelButtonTitle: "Okay")
            alert.show()
        } else {
            deBorderTextField(userCredentialField!)
            changeLabelText("Loading...")
            var target: String = userCredentialField!.text!
            var type = 2
            if accountTypePhone {
                type = 1
                target = stripPhoneNumber(target)
            }
            loginToStatus()
            
            addPoints(target, type: type, dollars: dollars)
        }
    }
    func showSignUpHandler() {
        loginToSignUp()
    }
    func signUpHandler(_ dollars: Double) {
        if (userCredentialField!.text == "" || fullNameField!.text == "") {
            if userCredentialField!.text == "" && userCredentialField!.text == "" {
                borderTextField(userCredentialField!)
                borderTextField(fullNameField!)
                let alert = UIAlertView(title: "Error", message: "Please enter your information!", delegate: nil, cancelButtonTitle: "Okay")
                alert.show()
            } else if userCredentialField!.text == "" {
                borderTextField(userCredentialField!)
                deBorderTextField(fullNameField!)
                let alert = UIAlertView(title: "Error", message: "Please enter your user credentials!", delegate: nil, cancelButtonTitle: "Okay")
                alert.show()
            } else if fullNameField!.text == "" {
                borderTextField(fullNameField!)
                deBorderTextField(userCredentialField!)
                let alert = UIAlertView(title: "Error", message: "Please enter your name!", delegate: nil, cancelButtonTitle: "Okay")
                alert.show()
            }
        } else if accountTypePhone && stripPhoneNumber(userCredentialField!.text!).characters.count < 10 {
            borderTextField(userCredentialField!)
            deBorderTextField(fullNameField!)
            let alert = UIAlertView(title: "Error", message: "Please enter a valid phone number!", delegate: nil, cancelButtonTitle: "Okay")
            alert.show()
        } else {
            deBorderTextField(fullNameField!)
            deBorderTextField(userCredentialField!)
            changeLabelText("Loading...")
            var target: String = userCredentialField!.text!
            let name: String = fullNameField!.text!
            var type = 2
            if accountTypePhone {
                type = 1
                target = stripPhoneNumber(target)
            }
            signUpToStatus()
            createAccount(target, type: type, fullName: name, dollars: dollars)
        }
    }
    func cancelSignUpHandler() {
        signUpToLogin()
    }
    func getDollarsForLogin() {
        if !useDollars {
            loginHandler(-1)
            return
        }
        var dollars: Double? = nil
        let alert = UIAlertController(title: "Get Dollar Amount", message: "How many dollars were spent?", preferredStyle: .alert)
        alert.addTextField { (textField: UITextField!) -> Void in
            textField.placeholder = "Dollar Amount"
            textField.keyboardAppearance = .dark
            textField.keyboardType = .decimalPad
        }
    
        alert.addTextField { (textField: UITextField!) -> Void in
            textField.placeholder = "Store PIN"
            textField.isSecureTextEntry = true
            textField.keyboardType = .numberPad
            textField.keyboardAppearance = .dark
        }
        alert.addAction(UIAlertAction(title: "Cancel", style: .cancel, handler: nil))
        alert.addAction(UIAlertAction(title: "Redeem", style: .default, handler: { (action: UIAlertAction) -> Void in
            let pinField: UITextField = alert.textFields![1] 
            let dollarField: UITextField = alert.textFields![0] 
            let pin = pinField.text
            
            //let dollars = dollarField.text.toInt()
            if pin != "" && dollarField.text != "" {
                if pin != self.username! {
                    let alert = UIAlertView(title: "Error", message: "Incorrect Pin", delegate: nil, cancelButtonTitle: "Okay")
                    alert.show()
                } else {
                    dollars = NSString(string: dollarField.text!).doubleValue
                    self.loginHandler(dollars!)
                }
            } else {
                let alert = UIAlertView(title: "Error", message: "Please Fill In All Fields", delegate: nil, cancelButtonTitle: "Okay")
                alert.show()
                
            }
        }))
        present(alert, animated: true, completion: nil)
        
        

    }
    func getDollarsForSignUp(){
        if !useDollars {
            signUpHandler(-1)
            return
        }
        var dollars: Double? = nil
        let alert = UIAlertController(title: "Get Dollar Amount", message: "How many dollars were spent?", preferredStyle: .alert)
        alert.addTextField { (textField: UITextField!) -> Void in
            textField.placeholder = "Dollar Amount"
            textField.keyboardAppearance = .dark
            textField.keyboardType = .decimalPad
        }
        
        alert.addTextField { (textField: UITextField!) -> Void in
            textField.placeholder = "Store PIN"
            textField.isSecureTextEntry = true
            textField.keyboardType = .numberPad
            textField.keyboardAppearance = .dark
        }
        alert.addAction(UIAlertAction(title: "Cancel", style: .cancel, handler: nil))
        alert.addAction(UIAlertAction(title: "Redeem", style: .default, handler: { (action: UIAlertAction) -> Void in
            let pinField: UITextField = alert.textFields![1] 
            let dollarField: UITextField = alert.textFields![0] 
            let pin = pinField.text
            
            //let dollars = dollarField.text.toInt()
            if pin != "" && dollarField.text != "" {
                if pin != self.username! {
                    let alert = UIAlertView(title: "Error", message: "Incorrect Pin", delegate: nil, cancelButtonTitle: "Okay")
                    alert.show()
                } else {
                    dollars = NSString(string: dollarField.text!).doubleValue
                    self.signUpHandler(dollars!)
                }
            } else {
                let alert = UIAlertView(title: "Error", message: "Please Fill In All Fields", delegate: nil, cancelButtonTitle: "Okay")
                alert.show()
                
            }
        }))
        present(alert, animated: true, completion: nil)
        

    }
    
    //
    // GRAPHICS - graphics changes, animations, all dat jazz
    //
    func changeLabelText(_ text: String) {
        UIView.beginAnimations(nil, context: nil)
        UIView.setAnimationCurve(.easeIn)
        UIView.setAnimationDelegate(self)
        UIView.setAnimationDuration(0.25)
        disableSubview(mainLabel!)
        UIView.commitAnimations()
        mainLabel!.text = text
        UIView.beginAnimations(nil, context: nil)
        UIView.setAnimationCurve(.easeIn)
        UIView.setAnimationDelegate(self)
        UIView.setAnimationDuration(0.25)
        enableSubview(mainLabel!)
        UIView.commitAnimations()
    }
    func loginToStatus() {
        UIView.beginAnimations(nil, context: nil)
        UIView.setAnimationCurve(.easeIn)
        UIView.setAnimationDelegate(self)
        UIView.setAnimationDuration(0.3)
        disableSubview(userCredentialField!)
        disableSubview(accountTypeController!)
        disableSubview(loginButton!)
        disableSubview(showSignUpScreenButton!)
        disableSubview(cancelLoginButton!)
        disableSubview(redeemCouponButton!)
        disableSubview(promoTextLabel!)
        UIView.commitAnimations()
        
        UIView.beginAnimations(nil, context: nil)
        UIView.setAnimationCurve(.easeIn)
        UIView.setAnimationDelegate(self)
        UIView.setAnimationDuration(0.3)
        enableSubview(mainLabel!)
        UIView.commitAnimations()
    }
    func loginToSignUp() {
        isSigningUp = true
        UIView.beginAnimations(nil, context: nil)
        UIView.setAnimationCurve(.easeIn)
        UIView.setAnimationDelegate(self)
        UIView.setAnimationDuration(0.3)
        disableSubview(logoImageView!)
        disableSubview(loginButton!)
        disableSubview(showSignUpScreenButton!)
        disableSubview(redeemCouponButton!)
        disableSubview(cancelLoginButton!)
        disableSubview(promoTextLabel!)
        deBorderTextField(userCredentialField!)
        UIView.commitAnimations()
        
        UIView.beginAnimations(nil, context: nil)
        UIView.setAnimationCurve(.easeIn)
        UIView.setAnimationDelegate(self)
        UIView.setAnimationDuration(0.3)
        drawFrames(nil)
        enableSubview(fullNameField!)
        enableSubview(signUpButton!)
        enableSubview(cancelSignUpButton!)
        enableSubview(canSpamLabel!)
        UIView.commitAnimations()
    }
    func signUpToLogin() {
        isSigningUp = false
        UIView.beginAnimations(nil, context: nil)
        UIView.setAnimationCurve(.easeIn)
        UIView.setAnimationDelegate(self)
        UIView.setAnimationDuration(0.3)
        drawFrames(nil)
        disableSubview(fullNameField!)
        disableSubview(signUpButton!)
        disableSubview(cancelSignUpButton!)
        disableSubview(canSpamLabel!)
        deBorderTextField(userCredentialField!)
        deBorderTextField(fullNameField!)
        UIView.commitAnimations()
        
        UIView.beginAnimations(nil, context: nil)
        UIView.setAnimationCurve(.easeIn)
        UIView.setAnimationDelegate(self)
        UIView.setAnimationDuration(0.3)
        enableSubview(logoImageView!)
        enableSubview(loginButton!)
        enableSubview(showSignUpScreenButton!)
        enableSubview(redeemCouponButton!)
        //enableSubview(cancelLoginButton!)
        enableSubview(promoTextLabel!)
        UIView.commitAnimations()
    }
    func loginToScanner() {
        UIView.beginAnimations(nil, context: nil)
        UIView.setAnimationCurve(.easeIn)
        UIView.setAnimationDelegate(self)
        UIView.setAnimationDuration(0.3)
        disableSubview(logoImageView!)
        disableSubview(userCredentialField!)
        disableSubview(accountTypeController!)
        disableSubview(loginButton!)
        disableSubview(showSignUpScreenButton!)
        disableSubview(cancelLoginButton!)
        disableSubview(promoTextLabel!)
        UIView.commitAnimations()
        
        UIView.beginAnimations(nil, context: nil)
        UIView.setAnimationCurve(.easeIn)
        UIView.setAnimationDelegate(self)
        UIView.setAnimationDuration(0.3)
        //enable scanner
        enableSubview(showLoginScreenButton!)
        UIView.commitAnimations()
    }
    func scannerToLogin() {
        UIView.beginAnimations(nil, context: nil)
        UIView.setAnimationCurve(.easeIn)
        UIView.setAnimationDelegate(self)
        UIView.setAnimationDuration(0.3)
        //disable scanner
        disableSubview(showLoginScreenButton!)
        UIView.commitAnimations()
        
        UIView.beginAnimations(nil, context: nil)
        UIView.setAnimationCurve(.easeIn)
        UIView.setAnimationDelegate(self)
        UIView.setAnimationDuration(0.3)
        enableSubview(logoImageView!)
        enableSubview(userCredentialField!)
        enableSubview(accountTypeController!)
        enableSubview(loginButton!)
        enableSubview(showSignUpScreenButton!)
        //enableSubview(cancelLoginButton!)
        enableSubview(promoTextLabel!)
        UIView.commitAnimations()
    }
    func signUpToStatus() {
        isSigningUp = false
        UIView.beginAnimations(nil, context: nil)
        UIView.setAnimationCurve(.easeIn)
        UIView.setAnimationDelegate(self)
        UIView.setAnimationDuration(0.3)
        disableSubview(userCredentialField!)
        disableSubview(accountTypeController!)
        disableSubview(fullNameField!)
        disableSubview(signUpButton!)
        disableSubview(cancelSignUpButton!)
        disableSubview(canSpamLabel!)
        UIView.commitAnimations()
        
        UIView.beginAnimations(nil, context: nil)
        UIView.setAnimationCurve(.easeIn)
        UIView.setAnimationDelegate(self)
        UIView.setAnimationDuration(0.3)
        drawFrames(nil)
        enableSubview(logoImageView!)
        enableSubview(mainLabel!)
        UIView.commitAnimations()
    }
    func statusToScanner() {
       
        UIView.beginAnimations(nil, context: nil)
        UIView.setAnimationCurve(.easeIn)
        UIView.setAnimationDelegate(self)
        UIView.setAnimationDuration(0.3)
        disableSubview(mainLabel!)
        //disableSubview(logoImageView!)
        UIView.commitAnimations()
        
        UIView.beginAnimations(nil, context: nil)
        UIView.setAnimationCurve(.easeIn)
        UIView.setAnimationDelegate(self)
        UIView.setAnimationDuration(0.3)
        // enable scanner
        enableSubview(redeemCouponButton!)
        //enableSubview(showLoginScreenButton!)
        UIView.commitAnimations()
        
        //
        // UNTIL SCANNER IMPLEMENTED
        //
        scannerToLogin()
    }
    func scannerToStatus() {
        UIView.beginAnimations(nil, context: nil)
        UIView.setAnimationCurve(.easeIn)
        UIView.setAnimationDelegate(self)
        UIView.setAnimationDuration(0.3)
        // disable scanner
        disableSubview(redeemCouponButton!)
        disableSubview(showLoginScreenButton!)
        UIView.commitAnimations()
        
        UIView.beginAnimations(nil, context: nil)
        UIView.setAnimationCurve(.easeIn)
        UIView.setAnimationDelegate(self)
        UIView.setAnimationDuration(0.3)
        enableSubview(mainLabel!)
        enableSubview(logoImageView!)
        UIView.commitAnimations()
    }
}

