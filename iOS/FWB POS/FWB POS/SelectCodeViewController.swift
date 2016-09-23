//
//  SelectCodeViewController.swift
//  FWB POS
//
//  Created by Ben Grass on 4/11/15.
//  Copyright (c) 2015-16 Barsoft. All rights reserved.
//

import UIKit

class SelectCodeViewController: UIViewController, UICollectionViewDelegate, UICollectionViewDataSource {
    var offers: Array<(String, String, Int, Int)>!
    var offerCollectionView: UICollectionView!
    var name: String!
    var points: Int!
    var backgroundColor: UIColor!
    var highlightColor: UIColor!
    var sender: ViewController!
    var target: Int!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setUpElements()

    }
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
    }
    
    override var shouldAutorotate : Bool {
        return false
    }
    func collectionView(_ collectionView: UICollectionView, numberOfItemsInSection section: Int) -> Int {
        return offers.count
    }
    override var prefersStatusBarHidden : Bool {
        return true
    }
    
    func setUp(_ offers: Array<(String, String, Int, Int)>, target: Int, name: String, points: Int, backgroundColor: UIColor, highlightColor: UIColor, sender: ViewController) {
        self.target = target
        self.offers = offers
        self.name = name
        self.points = points
        self.backgroundColor = backgroundColor
        self.highlightColor = highlightColor
        self.sender = sender
    }
    
    func setUpElements() {
        view.backgroundColor = backgroundColor
        
        let layout = KTCenterFlowLayout()
        layout.itemSize = CGSize(width: 200, height: 200)
        layout.sectionInset = UIEdgeInsets(top: 20, left: 20, bottom: 20, right: 20)
        layout.minimumInteritemSpacing = 20
        layout.minimumLineSpacing = 20
        offerCollectionView = UICollectionView(frame: CGRect(x: 0, y: 0.15 * self.view.frame.size.height, width: self.view.frame.size.width, height: 0.7 * self.view.frame.size.height), collectionViewLayout: layout)
        offerCollectionView.register(CodeCell.self, forCellWithReuseIdentifier: "Cell")
        offerCollectionView.backgroundColor = UIColor(white: 0, alpha: 0.1)
        offerCollectionView.delegate = self
        offerCollectionView.dataSource = self
        view.addSubview(offerCollectionView)
        
        let topLabel = UILabel(frame: CGRect(x: 20, y: 0, width: self.view.frame.size.width - 40, height: 0.15*self.view.frame.size.height))
        topLabel.text = "You have \(points) points!\nPlease select a benefit."
        topLabel.textColor = highlightColor
        topLabel.font = UIFont.boldSystemFont(ofSize: 25)
        topLabel.numberOfLines = 2
        topLabel.textAlignment = .center
        topLabel.lineBreakMode = .byWordWrapping
        self.view.addSubview(topLabel)
        
        let selectNoneButton = UIButton(frame: CGRect(x: self.view.frame.size.width/3, y: 0.87*self.view.frame.size.height, width: self.view.frame.size.width/3, height: 0.11*self.view.frame.size.height))
        selectNoneButton.setTitle("(Select None)", for: UIControlState())
        selectNoneButton.setTitleColor(self.highlightColor, for: UIControlState())
        selectNoneButton.backgroundColor = UIColor(white: 0, alpha: 0.3)
        selectNoneButton.layer.cornerRadius = 7
        selectNoneButton.layer.borderWidth = 2
        selectNoneButton.layer.borderColor = highlightColor.cgColor
        selectNoneButton.addTarget(self, action: #selector(SelectCodeViewController.selectNone), for: .touchUpInside)
        self.view.addSubview(selectNoneButton)
        
        /*
        signInButton = UIButton(frame: CGRect(x: 0.25 * self.view.frame.size.width, y: passwordField.frame.origin.y + passwordField.frame.size.height + yDist, width: 0.5 * self.view.frame.size.width, height: 2 * textFieldHeight))
        signInButton.setTitle("Sign In", forState: .Normal)
        signInButton.setTitleColor(UIColor.whiteColor(), forState: .Normal)
        signInButton.titleLabel!.font = UIFont.boldSystemFontOfSize(mainLabelTextSize)
        signInButton.backgroundColor = UIColor(white: 0, alpha: 0.3)
        signInButton.layer.cornerRadius = 10
        signInButton.layer.borderWidth = 3.25
        signInButton.layer.borderColor = UIColor.whiteColor().CGColor
        signInButton.addTarget(sender, action: "login:", forControlEvents: .TouchUpInside)
        self.view.addSubview(signInButton!)
        */

    }
    
    func collectionView(_ collectionView: UICollectionView, cellForItemAt indexPath: IndexPath) -> UICollectionViewCell {
        let offer = offers[(indexPath as NSIndexPath).item]
        let cell = collectionView.dequeueReusableCell(withReuseIdentifier: "Cell", for: indexPath) as! CodeCell
        
        var enabled = true
        if points - offer.2 < 0 {
            enabled = false
        }
        cell.setUp(offer.0, points: offer.2, desc: offer.1, color: highlightColor, enabled: enabled)
        
        return cell
    }

    func collectionView(_ collectionView: UICollectionView, didSelectItemAt indexPath: IndexPath) {
        let offer = offers[(indexPath as NSIndexPath).item]
        let newPoints = points - offer.2
        let alert = UIAlertController(title: "Select Offer", message: "Would you like to select \(offer.0)? You will have \(newPoints).", preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "Cancel", style: .cancel, handler: nil))
        alert.addAction(UIAlertAction(title: "Select", style: .default, handler: { (action: UIAlertAction) -> Void in
            self.sender.selectOffer(self.target, id: offer.3)
        }))
        present(alert, animated: true, completion: nil)
        
    }
    
    func selectNone() {
        sender.didNotSelectOffer(name, points: points)
    }
}
