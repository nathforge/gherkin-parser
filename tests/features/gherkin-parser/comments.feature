    # language: en
                                                                      # comment
    # language: ignored
                                                                      # comment
    @ftag1 @ftag2                                                     # comment
                                                                      # comment
    @ftag3 @ftag4                                                     # comment
                                                                      # comment
    Feature: ftitle # unparsed comment
                                                                      # comment
        fdesc1                                                        # comment
                                                                      # comment
        fdesc2                                                        # comment
                                                                      # comment
            fdesc3                                                    # comment
                                                                      # comment
            and                                                       # comment
                                                                      # comment
            but                                                       # comment
                                                                      # comment
        Background: btitle # unparsed comment
                                                                      # comment
            bdesc1                                                    # comment
                                                                      # comment
            bdesc2                                                    # comment
                                                                      # comment
                bdesc3                                                # comment
                                                                      # comment
                and                                                   # comment
                                                                      # comment
                but                                                   # comment
                                                                      # comment
            Given bgiven                                              # comment
                                                                      # comment
            When  bwhen                                               # comment
                                                                      # comment
            Then  bthen                                               # comment
                                                                      # comment
        @stag1 @stag2                                                 # comment
                                                                      # comment
        @stag3 @stag4                                                 # comment
                                                                      # comment
        Scenario: stitle # unparsed comment
                                                                      # comment
            sdesc1                                                    # comment
                                                                      # comment
            sdesc2                                                    # comment
                                                                      # comment
                sdesc3                                                # comment
                                                                      # comment
                and                                                   # comment
                                                                      # comment
                but                                                   # comment
                                                                      # comment
            Given sgiven1                                             # comment
                                                                      # comment
            Given sgiven2                                             # comment
                                                                      # comment
            And   sgiven3                                             # comment
                                                                      # comment
            But   sgiven4                                             # comment
                                                                      # comment
                """
                sgiven4text1     # unparsed comment

                sgiven4text2     # unparsed comment
                
                    sgiven4text3 # unparsed comment
                """
                                                                      # comment
                | a    | b    | c    |
                                                                      # comment
                | 1 \| | 2 \| | 3 \| |
                                                                      # comment
            When swhen1                                               # comment
                                                                      # comment
            When swhen2                                               # comment
                                                                      # comment
            And  swhen3                                               # comment
                                                                      # comment
            But  swhen4                                               # comment
                                                                      # comment
                """
                swhen4text1     # unparsed comment

                swhen4text2     # unparsed comment
                
                    swhen4text3 # unparsed comment
                """
                                                                      # comment
                | a    | b    | c    |
                                                                      # comment
                | 1 \| | 2 \| | 3 \| |
                                                                      # comment
            Then sthen1                                               # comment
                                                                      # comment
            Then sthen2                                               # comment
                                                                      # comment
            And  sthen3                                               # comment
                                                                      # comment
            But  sthen4                                               # comment
                                                                      # comment
                """
                sthen4text1     # unparsed comment

                sthen4text2     # unparsed comment
                
                    sthen4text3 # unparsed comment
                """
                                                                      # comment
                | a    | b    | c    |
                                                                      # comment
                | 1 \| | 2 \| | 3 \| |
                                                                      # comment
        Scenario Outline: sotitle # unparsed comment
                                                                      # comment
            sodesc1                                                   # comment
                                                                      # comment
            sodesc2                                                   # comment
                                                                      # comment
                sodesc3                                               # comment
                                                                      # comment
                and                                                   # comment
                                                                      # comment
                but                                                   # comment
                                                                      # comment
            Given sogiven                                             # comment
                                                                      # comment
            When  sowhen                                              # comment
                                                                      # comment
            Then  sothen                                              # comment
                                                                      # comment
            Examples: etitle # unparsed comment
                                                                      # comment
                | a    | b    | c    |
                                                                      # comment
                | 1 \| | 2 \| | 3 \| |
                                                                      # comment
