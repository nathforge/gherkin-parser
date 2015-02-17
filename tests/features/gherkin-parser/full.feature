# language: en

@tag1 @tag2
@tag3
Feature: Title
    Desc 1
    Desc 2
        Desc 3

    Background: Title
        Given given
            | key  | value |
            | name | Test  |
        When when
            """
            Text
                test
            """
        Then then
            '''
            Text
                test
            '''    

    # Empty scenario title
    Scenario:

    # Empty scenario content
    Scenario: Empty scenario

    # Full scenario
    @tag1 @tag2
    @tag3
    Scenario: Scenario
        Desc 1
        Desc 2
            Desc 3

        Given given
            | key  | value |
            | name | Test  |
        When when
            """
            Text
                test
            """
        Then then
            '''
            Text
                test
            '''

    # Empty scenario outline
    Scenario Outline:
        Examples:

    # Empty scenario outline with title
    Scenario Outline: Empty scenario outline
        Examples:

    # Full scenario outline
    @tag1 @tag2
    @tag3
    Scenario Outline: Scenario Outline
        Desc 1
        Desc 2
            Desc 3

        Given given <key> is <value>
            | key  | value |
            | name | Test  |
        When when <key> is <value>
            """
            Text
                <key>
            """
        Then then <key> is <value>
            '''
            Text
                <key>
            '''

        Examples: Example title
            | key  | value |
            | name | Test  |
  