; Brendan Fay
; bfay@stevens.edu
; School of Systems and Enterprises
; Stevens Institute of Technology

globals
[
  product-1-attributes  ;
  product-2-attributes  ;
  product-3-attributes  ;
  product-4-attributes  ;
  product-5-attributes  ;
  attribute-kano-types  ;
  max-lifespan          ;
  days                  ; The amount of days that have passed in the similation
  consumer-scale        ; The number of actual consumers represented by 1 consumer in the simulation
]
breed [ producers producer ]
breed [ consumers consumer ]

producers-own [
  product-attributes  ; A list of attribute values for this producer's product
  product-lifespan    ; The average amount of time (in years) before the product breaks
  sales               ; The total amount of products that have been sold
  price               ; The price of the product
  consumer-count      ; The number of consumers
  ]
consumers-own [
    s       ; Randomly generated, based on normal distributions; used in utility function
  best-producer     ; The producer that this consumer last purchased a product from
  product-lifespan  ; The current lifespan of the product
  profit            ; Total profit accumulated
  ]

to setup
  clear-all


  ; find a reasonable maximum lifespan for the products (currently 10x the max lifespan listed)
  set max-lifespan ((max (list p1-life p2-life p3-life p4-life p5-life)) * 2.5 * 365)

  ; Normalize the attribute values on a scale of -1 to 1
  ; i.e. Price among all products: [0.25 -1 0.5 -0.75 1]
  let attribute-1-set (normalize (list p1-att-1 p2-att-1 p3-att-1 p4-att-1 p5-att-1))
  let attribute-2-set (normalize (list p1-att-2 p2-att-2 p3-att-2 p4-att-2 p5-att-2))
  let attribute-3-set (normalize (list p1-att-3 p2-att-3 p3-att-3 p4-att-3 p5-att-3))
  let attribute-4-set (normalize (list p1-att-4 p2-att-4 p3-att-4 p4-att-4 p5-att-4))
  let attribute-5-set (normalize (list p1-att-5 p2-att-5 p3-att-5 p4-att-5 p5-att-5))

  ; Assign the attribute values to the correct attribute list for each product
  ; i.e. Attributes for product 1: [0.25 -1 -1 1 0.8]
  set product-1-attributes (list (item 0 attribute-1-set) (item 0 attribute-2-set) (item 0 attribute-3-set) (item 0 attribute-4-set) (item 0 attribute-5-set))
  set product-2-attributes (list (item 1 attribute-1-set) (item 1 attribute-2-set) (item 1 attribute-3-set) (item 1 attribute-4-set) (item 1 attribute-5-set))
  set product-3-attributes (list (item 2 attribute-1-set) (item 2 attribute-2-set) (item 2 attribute-3-set) (item 2 attribute-4-set) (item 2 attribute-5-set))
  set product-4-attributes (list (item 3 attribute-1-set) (item 3 attribute-2-set) (item 3 attribute-3-set) (item 3 attribute-4-set) (item 3 attribute-5-set))
  set product-5-attributes (list (item 4 attribute-1-set) (item 4 attribute-2-set) (item 4 attribute-3-set) (item 4 attribute-4-set) (item 4 attribute-5-set))

  ;; Get the Kano curve types
  set attribute-kano-types (list kano-type-1 kano-type-2 kano-type-3 kano-type-4 kano-type-5)

  ;; Create the producers
  create-producers 5
  ask producers [
    setxy 24 (24 - who * 5 - 2)
    set shape "house"

    ;; Assign attributes, lifespan, and cost to each producer
    if (who = 0) [
      set product-attributes product-1-attributes
      set product-lifespan p1-life
      set price p1-att-1 ; Attribute 1 is always price in this simulation
      set sales 0
      set color red

      set consumer-count number-of-consumers ; Initially, all consumers are considered to be consumers of product 0
      ]
    if (who = 1) [
      set product-attributes product-2-attributes
      set product-lifespan p2-life
      set price p2-att-1
      set sales 0
      set color (yellow - 1)
      ]
    if (who = 2) [
      set product-attributes product-3-attributes
      set product-lifespan p3-life
      set price p3-att-1 ;;price
      set sales 0
      set color green
      ]
    if (who = 3) [
      set product-attributes product-4-attributes
      set product-lifespan p4-life
      set price p4-att-1 ;;price
      set sales 0
      set color blue
      ]
    if (who = 4) [
      set product-attributes product-5-attributes
      set product-lifespan p5-life
      set price p5-att-1 ;;price
      set sales 0
      set color magenta
      ]
  ]

  ;; Create the consumers
  create-consumers number-of-consumers
  ask consumers [
    setxy random-xcor 0
    set shape "person"
    set color 5
    set best-producer 0      ; Initially, all consumers are considered to be consumers of product 0
    set product-lifespan -1  ; A lifespan of less than 0 means the consumer no longer owns a product

    ;; Create the preferences for the consumer, based on the given standard deviation value and a mean of 1, and multiply by attribute weight
    ;; Precision is capped to 3 decimial points to avoid excessive calculations
    set preferences (list
      ((precision (random-lognormal 1 stddev-1) 3) * weight-1)
      ((precision (random-lognormal 1 stddev-2) 3) * weight-2)
      ((precision (random-lognormal 1 stddev-3) 3) * weight-3)
      ((precision (random-lognormal 1 stddev-4) 3) * weight-4)
      ((precision (random-lognormal 1 stddev-5) 3) * weight-5)
      )
  ]

  set days 1 ;; Avoids calculation errors in first tick when days=0
  set consumer-scale (buyers-in-market / number-of-consumers) ;; Define number of real-world consumers represented by each consumer in the model

  reset-ticks
end

to step
  go
end

to go
  ask consumers [
    ;; Purchase a product, if they don't already have one
    if (product-lifespan < 0) [
      purchase-product
    ]

    ; Update the position of the consumer based on the consumer's product's remaining lifespan
    setxy (24 - floor ((product-lifespan / max-lifespan) * 24)) ycor

    ; Decrement the lifespan of the product accordingly
    set product-lifespan (product-lifespan - days-per-tick)
  ]

  ; ignore first few sales, which determine the initial product of each consumer
  if (ticks < 10) [
    ask producers [ set sales 0]
  ]

  ;;display ; Update UI forcibly (Slows down the simulation)
  set days (ticks * days-per-tick + 1) ; Update the amount of days that have elapsed
  tick ; Update plot
end

to purchase-product
  ;;
  let max-utility -100000          ; Arbitrarily low number
  let last-producer best-producer  ; Keep track of last best producer, for counting purposes

  ; The consumer goes through each producer and calculates the utility of their product
  foreach sort producers [
    let temp-utility 0

    ;; UTILITY FUNCTION
    ; Find utility for each attribute, and sum them up into temp-utility
    (foreach ([product-attributes] of ?) preferences attribute-kano-types [ ; 1? - product attribute, ?2 - preference, ?3 - kano type
        if (?3 = "delighter") [
          set temp-utility (temp-utility + ?2 * e ^ (2 * ?1 - 1))
        ]
        if (?3 = "satisfier") [
          set temp-utility (temp-utility + ?2 * ?1)
        ]
        if (?3 = "basic") [
          set temp-utility (temp-utility + ?2 * (0 - e ^ (-2 * ?1 - 1)))
        ]
        if (?3 = "delighter (reversed)") [
          set temp-utility (temp-utility + ?2 * e ^ (-2 * ?1 - 1))
        ]
        if (?3 = "satisfier (reversed)") [
          set temp-utility (temp-utility - ?2 * ?1)
        ]
        if (?3 = "basic (reversed)") [
          set temp-utility (temp-utility + ?2 * (0 - e ^ (2 * ?1 - 1)))
        ]
      ])

    ;; Ignore the new product if applicable by setting its temp-utility to default value
    if ([who] of ?) = 0 [
      if include-new-product = false [
        set temp-utility -100000
      ]
    ]
    ;; Ignore other products if applicable as well
    if ([who] of ?) = 1 [
      if include-c1 = false [
        set temp-utility -100000
      ]
    ]
    if ([who] of ?) = 2 [
      if include-c2 = false [
        set temp-utility -100000
      ]
    ]
    if ([who] of ?) = 3 [
      if include-c3 = false [
        set temp-utility -100000
      ]
    ]
    if ([who] of ?) = 4 [
      if include-c4 = false [
        set temp-utility -100000
      ]
    ]
    ;; /UTILITY FUNCTION

    ; Set new best product if its utility is highest
    if (temp-utility > max-utility) [
      set max-utility temp-utility
      set best-producer ([who] of ?)
    ]
  ]

  ; Set the color, product lifespan, and vertical of this consumer to that of the chosen producer
  ; The color is adjusted by +/- 3 to differentiate consumers
  ; The lifespan (when the product will fail/disappear) is exponentially distributed
  set product-lifespan ((random-exponential 1) * ([product-lifespan] of producer best-producer) * 365)
  set color ([color] of producer best-producer + (random 6 - 2))
  setxy xcor (20 - ([who] of producer best-producer) * 5 + (random 5))

  ; Update producer sales
  ask producer last-producer [
    set consumer-count (consumer-count - 1)  ; Decrease consumer count of the last producer
  ]
  ask producer best-producer [
    set sales (sales + 1)
    set consumer-count (consumer-count + 1)  ; Increase consumer count of the current producer
  ]

end

;; Normalizes a list of 5 numbers, returning a 5 number list with values scaled from -1 to 1
to-report normalize [ att-list ]
  let index-list (list 0 1 2 3 4)
  let new-list (list 0 0 0 0 0)
  let list-max max att-list
  let list-min min att-list
  if (list-min = list-max) [
    report att-list
  ]

  (foreach att-list index-list [
    set new-list replace-item ?2 new-list (precision ((2 * (?1 - list-min) / (list-max - list-min)) - 1) 3) ;; Use precision to avoid large decimal place counts
  ])
  report new-list
end

;; Creates a lognormally distributed number based on the mean and variance of the population
to-report random-lognormal [ mn var ]
  let mu ((ln (mn ^ 2)) / (sqrt (var + (mn ^ 2))))
  let sigma (sqrt (ln (1 + (var / (mn ^ 2)))))
  report (e ^ (random-normal mu sigma))
end

;; Reports the yearly profit of a producer
to-report daily-profit-of-producer [ producer-number ]
  report (([sales] of producer producer-number) * ([price] of producer producer-number) * consumer-scale / days)
end

;; Reports the yearly profit of a producer
to-report monthly-profit-of-new-product
  report ([sales] of producer 0 * (p1-att-1 - p1-cost) * consumer-scale) / (current-month)
end

;; Reports the current year of the simulation
to-report current-year
  report (days / 365)
end

;; Reports the current month of the simulation
to-report current-month
  report (days * 12 / 365)
end

;; Reports the number of consumers that have purchased a product from a producer
to-report consumer-count-of-producer [ producer-number ]
  report (([consumer-count] of producer producer-number) * consumer-scale)
end

to-report consumer-count-histogram
  report (list (consumer-count-of-producer 0)
    (consumer-count-of-producer 1)
    (consumer-count-of-producer 2)
    (consumer-count-of-producer 3)
    (consumer-count-of-producer 4))
end

to-report months-per-tick
  report days-per-tick * 12 / 365
end