//
//  CodeCell.swift
//  FWB POS
//
//  Created by Ben Grass on 4/11/15.
//  Copyright (c) 2015 Barsoft. All rights reserved.
//

import UIKit

class CodeCell: UICollectionViewCell {
    var offer: String!
    var points: Int!
    var desc: String!
    var color: UIColor!
    var enabled: Bool!
    var pointsLabel: UILabel? = nil
    var nameLabel: UILabel? = nil
    var descriptionLabel: UILabel? = nil
  
    
    override init(frame: CGRect) {
        super.init(frame: frame)
        layer.cornerRadius = 4
        layer.borderWidth = 2
        pointsLabel = UILabel(frame: CGRect(x: 10, y: 10, width: 180, height: 40))
        pointsLabel!.adjustsFontSizeToFitWidth = true
        pointsLabel!.textAlignment = .center
        pointsLabel!.font = UIFont.boldSystemFont(ofSize: 20)
        self.addSubview(pointsLabel!)
        nameLabel = UILabel(frame: CGRect(x: 10, y: 60, width: 180, height: 40))
        nameLabel!.adjustsFontSizeToFitWidth = true
        nameLabel!.textAlignment = .center
        nameLabel!.font = UIFont.boldSystemFont(ofSize: 20)
        self.addSubview(nameLabel!)
        descriptionLabel = UILabel(frame: CGRect(x: 10, y: 110, width: 180, height: 80))
        descriptionLabel!.adjustsFontSizeToFitWidth = true
        descriptionLabel!.numberOfLines = 4
        descriptionLabel!.textAlignment = .center
        descriptionLabel!.font = UIFont.boldSystemFont(ofSize: 20)
        self.addSubview(descriptionLabel!)
    }

    required init?(coder aDecoder: NSCoder) {
        super.init(coder: aDecoder)
    }
    
    
    
    func setUp(_ offer: String, points: Int, desc: String, color: UIColor, enabled: Bool) {
        self.offer = offer
        self.points = points
        self.desc = desc
        self.color = color
        self.enabled = enabled
        layer.borderColor = color.cgColor
        isUserInteractionEnabled = enabled
        if enabled == true {
            self.backgroundColor = UIColor(white: 0, alpha: 0.3)
        } else  {
            alpha = 0.5
            //self.backgroundColor = UIColor(white: 0, alpha: 0)
        }
        pointsLabel!.text = "\(points.description) Points"
        pointsLabel!.textColor = color
        nameLabel!.text = offer
        nameLabel!.textColor = color
        descriptionLabel!.text = desc
        descriptionLabel!.textColor = color
    }

    
    
}
