#pragma once

#include "ASTRule.h"

class NakedNewRule : public ASTRule,
                     public clang::ast_matchers::MatchFinder::MatchCallback
{
public:
    NakedNewRule(Context& context);

    void RegisterASTMatcherCallback(clang::ast_matchers::MatchFinder& finder) override;

    void run(const clang::ast_matchers::MatchFinder::MatchResult& Result) override;

private:
    clang::ast_matchers::StatementMatcher m_matcher;
};
